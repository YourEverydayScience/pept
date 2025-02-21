

![version](https://img.shields.io/badge/version-0.1.2-blue)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1G8XHP9zWMMDVu23PXzANLCOKNP_RjBEO)
[![docs](https://img.shields.io/badge/docs-docs-success)](https://uob-positron-imaging-centre.github.io)

# PEPT


A Python library that integrates all the tools necessary to
perform research using Positron Emission Particle Tracking (PEPT). The library
includes algorithms for the location, identification and tracking of particles,
in addition to tools for visualisation and analysis, and utilities allowing the
realistic simulation of PEPT data.


## Positron Emission Particle Tracking
PEPT is a technique developed at the University of Birmingham which allows the
non-invasive, three-dimensional tracking of one or more 'tracer' particles through
particulate, fluid or multiphase systems. The technique allows particle or fluid
motion to be tracked with sub-millimetre accuracy and sub-millisecond temporal
resolution and, due to its use of highly-penetrating 511keV gamma rays, can be
used to probe the internal dynamics of even large, dense, optically opaque
systems - making it ideal for industrial as well as scientific applications.


## Getting Started

These instructions will help you get started PEPT data analysis.

### Prerequisites

This package supports Python 3. You also need to have `NumPy` and `Cython`
on your system in order to install it.

### Installation

You can install `pept` from PyPI:

```
pip install pept
```

Or you can install the latest version from the GitHub repository:

```
pip install git+https://github.com/uob-positron-imaging-centre/pept
```

### Example usage

You can download data samples from the [UoB Positron Imaging Centre's
Repository](https://github.com/uob-positron-imaging-centre/example_data):

```
$> git clone https://github.com/uob-positron-imaging-centre/example_data
```

A minimal analysis script using the `pept.tracking.peptml` subpackage:

```
import pept
from pept.scanners import ParallelScreens
from pept.tracking import peptml
from pept.visualisation import PlotlyGrapher

lors = ParallelScreens('example_data/sample_2p_42rpm.csv', skiprows = 16)

max_distance = 0.1
cutpoints = peptml.Cutpoints(lors, max_distance)

clusterer = peptml.HDBSCANClusterer(min_sample_size = 30)
centres, clustered_cutpoints = clusterer.fit_cutpoints(cutpoints)

fig = PlotlyGrapher().create_figure()
fig.add_trace(centres.all_points_trace())
fig.show()
```

A more in-depth tutorial is available on [Google
Colab](https://colab.research.google.com/drive/1G8XHP9zWMMDVu23PXzANLCOKNP_RjBEO).

Full documentation is available [here](https://uob-positron-imaging-centre.github.io).


## Performance

Significant effort has been put into making the algorithms in this package as
fast as possible. The most compute-intensive parts have been implemented in
`C` and parallelised, where possible, using `joblib`. For example, using the `peptml`
subpackage, analysing 1,000,000 LoRs on the author's machine (mid 2012 MacBook Pro)
takes ~26 s (with another 12 s to read in the data). This efficiency is largely
due to the availabiliy of a great high-performance [implementation of the
HDBSCAN](https://github.com/scikit-learn-contrib/hdbscan) clustering algorithm.


## Help and Support

We recommend you check out [our tutorials](https://colab.research.google.com/drive/1G8XHP9zWMMDVu23PXzANLCOKNP_RjBEO). If your issue is not suitably resolved there, please
check the [issues](https://github.com/uob-positron-imaging-centre/pept/issues)
page on our GitHub. Finally, if no solution is available there, feel free to
[open an
issue](https://github.com/uob-positron-imaging-centre/pept/issues/new); the
authors will attempt to respond in a reasonably timely fashion.

## Contributing

We welcome contributions in any form! Assistance with documentation, particularly
expanding tutorials, is always welcome. To contribute please fork the project, make
your changes and submit a pull request. We will do our best to work through any
issues with you and get your code merged into the main branch.

## Licensing

The `pept` package is GNU v3.0 licensed.




