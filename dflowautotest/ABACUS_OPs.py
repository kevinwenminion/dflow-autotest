from typing import List
from dflow import (
    Workflow,
    Step,
    argo_range,
    SlurmRemoteExecutor,
    upload_artifact,
    download_artifact,
    InputArtifact,
    OutputArtifact,
    ShellOPTemplate
)
from dflow.python import (
    PythonOPTemplate,
    OP,
    OPIO,
    OPIOSign,
    Artifact,
    Slices,
    upload_packages
)
import time

import subprocess, os, shutil, glob, dpdata, pathlib
from pathlib import Path
from typing import List
from dflow.plugins.bohrium import BohriumContext, BohriumExecutor
from dpdata.periodic_table import Element
from monty.serialization import loadfn


from dflow.python import upload_packages

import shutil
upload_packages.append(__file__)

from .lib.utils import return_prop_list

class RelaxMakeABACUS(OP):
    """
    class for making calculation tasks
    """

    def __init__(self):
        pass

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input': Artifact(Path),
            'param': Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output': Artifact(Path),
            'njobs': int,
            'jobs': Artifact(List[Path])
        })

    @OP.exec_sign_check
    def execute(
            self,
            op_in: OPIO,
    ) -> OPIO:
        cwd = os.getcwd()

        os.chdir(op_in["input"])
        work_d = os.getcwd()
        param_argv = op_in["param"]
        structures = loadfn(param_argv)["structures"]
        cmd = f'dpgen autotest make {param_argv}'
        subprocess.call(cmd, shell=True)

        conf_dirs = []
        for conf in structures:
            conf_dirs.extend(glob.glob(conf))
        conf_dirs.sort()

        task_list = []
        for ii in conf_dirs:
            conf_dir_global = os.path.join(work_d, ii)
            task_list.append(os.path.join(conf_dir_global, 'relaxation/relax_task'))

        all_jobs = task_list
        njobs = len(all_jobs)
        jobs = []
        for job in all_jobs:
            jobs.append(pathlib.Path(job))

        os.chdir(cwd)
        op_out = OPIO({
            "output": op_in["input"],
            "njobs": njobs,
            "jobs": jobs
        })
        return op_out


class RelaxABACUS(OP):
    """
    class for ABACUS calculation
    """

    def __init__(self, infomode=1):
        self.infomode = infomode

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input_abacus': Artifact(Path),
            'run_command': str
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output_abacus': Artifact(Path, sub_path=False)
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        cwd = os.getcwd()
        os.chdir(op_in["input_abacus"])
        cmd = op_in["run_command"]
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
        op_out = OPIO({
            "output_abacus": op_in["input_abacus"]
        })
        return op_out


class RelaxPostABACUS(OP):
    """
    class for analyzing calculation results
    """

    def __init__(self):
        pass

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input_post': Artifact(Path, sub_path=False),
            'path': str,
            'input_all': Artifact(Path, sub_path=False),
            'param': Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output_all': Artifact(Path, sub_path=False),
            'output_confs': Artifact(Path, sub_path=False)
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        cwd = os.getcwd()
        os.chdir(str(op_in['input_all']) + op_in['path'])
        shutil.copytree(str(op_in['input_post']) + op_in['path'], './', dirs_exist_ok=True)

        param_argv = op_in['param']
        cmd = f'dpgen autotest post {param_argv}'
        subprocess.call(cmd, shell=True)

        os.chdir(cwd)
        shutil.copytree(str(op_in['input_all']) + op_in['path'] + '/confs', './confs', dirs_exist_ok=True)

        op_out = OPIO({
            'output_all': Path(str(op_in["input_all"]) + op_in['path']),
            'output_confs': Path('./confs')
        })
        return op_out


class PropsMakeABACUS(OP):
    """
    class for making calculation tasks
    """

    def __init__(self):
        pass

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input': Artifact(Path),
            'param': Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output': Artifact(Path),
            'njobs': int,
            'jobs': Artifact(List[Path])
        })

    @OP.exec_sign_check
    def execute(
            self,
            op_in: OPIO,
    ) -> OPIO:
        cwd = os.getcwd()

        os.chdir(op_in["input"])
        work_d = os.getcwd()
        param_argv = op_in["param"]
        structures = loadfn(param_argv)["structures"]
        inter_parameter = loadfn(param_argv)["interaction"]
        parameter = loadfn(param_argv)["properties"]
        cmd = f'dpgen autotest make {param_argv}'
        subprocess.call(cmd, shell=True)

        conf_dirs = []
        for conf in structures:
            conf_dirs.extend(glob.glob(conf))
        conf_dirs.sort()

        #from .lib.utils import return_prop_list
        prop_list = return_prop_list(parameter)
        task_list = []
        for ii in conf_dirs:
            conf_dir_global = os.path.join(work_d, ii)
            #for jj in prop_list:
            #    task_list.append(os.path.join(conf_dir_global, jj))
            for jj in prop_list:
                prop = os.path.join(conf_dir_global, jj)
                os.chdir(prop)
                prop_tasks = glob.glob(os.path.join(prop, 'task.*'))
                prop_tasks.sort()
                for kk in prop_tasks:
                    task_list.append(kk)

        all_jobs = task_list
        njobs = len(all_jobs)
        jobs = []
        for job in all_jobs:
            jobs.append(pathlib.Path(job))

        os.chdir(cwd)
        op_out = OPIO({
            "output": op_in["input"],
            "njobs": njobs,
            "jobs": jobs
        })
        return op_out


class PropsABACUS(OP):
    """
    class for ABACUS calculation
    """

    def __init__(self, infomode=1):
        self.infomode = infomode

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input_abacus': Artifact(Path),
            'run_command': str
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output_abacus': Artifact(Path, sub_path=False)
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        cwd = os.getcwd()
        os.chdir(op_in["input_abacus"])
        cmd = op_in["run_command"]
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
        op_out = OPIO({
            "output_abacus": op_in["input_abacus"]
        })
        return op_out


class PropsPostABACUS(OP):
    """
    class for analyzing calculation results
    """

    def __init__(self):
        pass

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            'input_post': Artifact(Path, sub_path=False),
            'path': str,
            'input_all': Artifact(Path, sub_path=False),
            'param': Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            'output_confs': Artifact(Path, sub_path=False)
        })

    @OP.exec_sign_check
    def execute(self, op_in: OPIO) -> OPIO:
        cwd = os.getcwd()
        os.chdir(str(op_in['input_all']) + op_in['path'])
        shutil.copytree(str(op_in['input_post']) + op_in['path'], './', dirs_exist_ok=True)

        param_argv = op_in["param"]
        cmd = f'dpgen autotest post {param_argv}'
        subprocess.call(cmd, shell=True)

        os.chdir(cwd)
        shutil.copytree(str(op_in['input_all']) + op_in['path'] + '/confs', './confs', dirs_exist_ok=True)

        op_out = OPIO({
            'output_confs': Path('./confs')
        })
        return op_out
