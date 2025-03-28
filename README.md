[![DOI](https://zenodo.org/badge/472438177.svg)](https://zenodo.org/badge/latestdoi/472438177)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md) 

**WARNING**: UPDATED to SIXTE calls for [SIXTE v 3.0 BETA](https://www.sternwarte.uni-erlangen.de/sixte/)

# SIXTE-tutorial
Jupyter notebooks to illustrate and document practical examples and exercises for the tutorial part of the [SIXTE](http://www.sternwarte.uni-erlangen.de/research/sixte/index.php) simulator manual.

To use these notebooks you must have SIXTE and [NASA's HEASOFT](https://heasarc.gsfc.nasa.gov/lheasoft/) installed and initiated.

You will find three different tutorials for each case. The first is for the old version of SIXTE, titled `tutorial-general-intro.ipynb.` The second is for the latest version of SIXTE, renamed `tutorial-general-intro-2.0.ipynb.` In both cases, make sure to set the XML paths and, if necessary, download files from the SIXTE website. The third version of the Jupyter notebook is designed for running on SciServer, titled `tutorial-general-intro_SciServer.ipynb`, where all paths and the environment are preconfigured. Additionally, some files required for running simulations are already available, so you won't need to download them.

It is also recommended to create a `conda` environment:

    >conda create --name tutorial python  
    >conda activate tutorial    
    >conda install matplotlib jupyterlab pandas astropy

In some environments you need to install also this package to avoid compatibility issues with xspec/heasoft:

    >conda install -c conda-forge gxx_linux-64==11.1.0  
    >conda install krb5 curl

A different set of additional packages may be required by your specific local configuration



