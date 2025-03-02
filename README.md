# dflow-props
## General properties test with VASP, ABACUS, and LAMMPS in autotest.
This workflow is a part of [AI Square](https://aissquare.com/). We want to refract the autotest code based on dflow. 
This is "general properties test" (elastic parameters, EOS, surface energy, interstitial energy, vacancy energy and stacking fault energy supported so far) using VASP, LAMMPS, or ABACUS.

## Easy Install：
```
pip install "git+https://github.com/ZLI-afk/dflow-autotest.git"
```

## Quick Start
You can go to the `example` folder and there are some examples for reference. You can go to one of them and fill in the `global.json` file. Then you can submit the workflow.

If you want to use VASP code to do the DFT autotest, like the folder `vasp_demo`. You need to prepare `INCAR`, `POTCAR`, `POSCAR`, `global.json`(notice that json files for relaxation and properties task are needed as input arguments), then ：
``` 
dflowprops param_relax.json param.props.json --vasp
```
If you want to run only relaxation or only propertie test (notice that properties test requires relaxation results under corresponding path under ./confs), for example of relaxation, just give one argument like:
``` 
dflowprops param_relax.json --vasp
```
This is same for the following case:

If you want to use ABACUS code, like the folder `abacus_demo`. You need to prepare `INPUT`, `STRU`, `*.UPF`, `global.json` and `param_prop.json` (notice that `*.orb` and `KPT` are optional ), then：
```
dflowprops param_relax.json param_props.json --abacus
```

If you want to use LAMMPS to do MD calculation, like the folder `dp_demo`. You need to prepare `POSCAR`, `frozen_model.pb`, `global.json` and `param_prop.json`, then:
```
dflowprops param_relax.json param_props.json --lammps
```

You can monitor the workflow process on the [website](https://workflows.deepmodeling.com).


