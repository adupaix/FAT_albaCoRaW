FAT albaCoRaW
===================
FAD Association by Tuna: A Lovely model BAsed on a COrrelated RAndom Walk

[![License](https://img.shields.io/github/license/adupaix/FAT_albaCoRaW)](https://github.com/adupaix/FAT_albaCoRaW/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/338344443.svg)](https://zenodo.org/badge/latestdoi/338344443)
[![Latest Release](https://img.shields.io/github/release/adupaix/FAT_albaCoRaW)](https://github.com/adupaix/FAT_albaCoRaW/releases)

---

__Individual based model simulating tuna trajectories in an array of Fish Aggregating Devices (FADs), based on a Correlated Random Walk.__

The model was calibrated using passive acoustic data acquired from 70 $\pm$ 10 cm yellowfin tuna (*Thunnus albacares*) tagged in Oahu (Hawaii, USA) and Mauritius (Pérez et al., [2022](https://doi.org/10.1016/j.ecolmodel.2022.110006)).

# Run

The model runs with [Python 3.8.5](https://docs.python.org/release/3.8.5/)

The [conda](https://docs.conda.io/projects/conda/en/latest/) environment to run the model is provided. To create, type : `conda env create -f env_CRW-model.yml`

To run the model, in the terminal, type:

`python cfg/ex_cgf.py` where `ex_cfg.py` is the configuration file (template available in the `cfg` folder)

# Plot

To plot tuna trajectories: run simulation in a Python environment. Then run `plot/PLOT_tuna_traj.py`, with r the id of the tuna of interest.

# References

Pérez, G., A. Dupaix, L. Dagorn, J.-L. Deneubourg, K. Holland, S. Beeharry, and M. Capello (2022). Correlated Random Walk of tuna in arrays of Fish Aggregating Devices: A field-based model from passive acoustic tagging. Ecological Modelling 470:110006. doi:[10.1016/j.ecolmodel.2022.110006](https://doi.org/10.1016/j.ecolmodel.2022.110006)
