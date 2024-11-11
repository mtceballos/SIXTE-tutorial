[![DOI](https://zenodo.org/badge/472438177.svg)](https://zenodo.org/badge/latestdoi/472438177)

**WARNING**: currently working in the update of SIXTE calls for [SIXTE v 3.0 BETA](https://www.sternwarte.uni-erlangen.de/sixte/)

# SIXTE-tutorial
Jupyter notebooks to illustrate and document practical examples and exercises for the tutorial part of the [SIXTE](http://www.sternwarte.uni-erlangen.de/research/sixte/index.php) simulator manual.

To use these notebooks you must have SIXTE and [NASA's HEASOFT](https://heasarc.gsfc.nasa.gov/lheasoft/) installed and initiated.

In addition, it is recommended that you create a `conda` environment:

    >conda create --name tutorial python  
    >conda activate tutorial    
    >conda install matplotlib jupyterlab pandas astropy

In some environments you need to install also this package to avoid compatibility issues with xspec/heasoft:

    >conda install -c conda-forge gxx_linux-64==11.1.0  
    >conda install krb5 curl

A different set of additional packages may be required by your specific local configuration



