# slf-extract-prv

[![PyPI - Version](https://img.shields.io/pypi/v/slf-extract-prv.svg)](https://pypi.org/project/slf-extract-prv)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/slf-extract-prv.svg)](https://pypi.org/project/slf-extract-prv)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

For now, clone the repository and install from there with pip:

```console
git clone https://github.com/rikuhuttunen/slf-extract-prv
cd slf-extract-prv
pip install -e .
```

## Extraction of PPG peaks and interpolation of IBI time series

The following command will extract the PPG peaks, interpolate the inter-beat-interval series, and save both to sleeplab-format sample arrays for all subjects in the dataset.

```console
python src/slf-extract-prv/extract_ibis.py --ds-dir <SLF DATASETDIRECTORY> \
    --ppg-key <THE NAME OF PPG SIGNAL> \
    --fs-interp <THE SAMPLING FREQUENCY OF THE INTERPOLATED IBI TIMESERIES> \
    --savedir <OPTIONAL SAVE DIRECTORY FOR THE PEAKS AND IBIS. IF NOT GIVEN, WILL SAVE IN THE SOURCE DATASET>
```

## License

`slf-extract-prv` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
