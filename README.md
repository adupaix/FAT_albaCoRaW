FAT albaCoRaW
===================
FAD Association by Tuna: A Lovely model BAsed on a COrrelated RAndom Walk

<!-- ![License](https://img.shields.io/github/license/CRW_model)

[![DOI](https://zenodo.org/badge/)](https://zenodo.org/badge/)

[![Latest Release](https://img.shields.io/github/release/CRW_model.svg)](https://github.com/CRW_model/releases) -->

---

Individual based model simulating tuna trajectories in an array of Fish Aggregating Devices (FADs), based on a Correlated Random Walk. This is the version of the model that was used to generate the results in the following publication:

Pérez G., Dupaix A., Dagorn L., Deneubourg J-L., Holland K., Beeharry S., Capello M. (in press). Correlated Random Walk of tuna in Fish Aggregating Device arrays: field-based model from acoustic tagging. __Ecological Modelling__

# Run

The model runs with [Python 3.8.5](https://docs.python.org/release/3.8.5/)

The [conda](https://docs.conda.io/projects/conda/en/latest/) environment to run the model is provided. To create, type : `conda env create -f env_CRW-model.yml`

To run the model, type:

`python cfg/ex_cgf.py` where `ex_cfg.py` is the configuration file (template available in the `cfg` folder)

# Plot

To plot tuna trajectories: run simulation in a Python environment. Then run `PLOT_tuna_traj.py`, with r the id of the tuna of interest.
