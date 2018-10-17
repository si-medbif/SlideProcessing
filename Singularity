Bootstrap: docker
From: ubuntu:18.04

%help
    Singularity image for DeepPATH
    

%labels
MAINTAINER dumrong.mai@biotec.or.th
Version v0.2

%post
    apt-get update && apt-get install -y --no-install-recommends \
            python-dev python-pip git openslide-tools \
            build-essential python-setuptools

    pip install --upgrade pip
    pip install numpy scipy wheel dicom openslide-python

    # Get DeepPATH scripts
    cd /opt && git clone https://github.com/ncoudray/DeepPATH.git
    apt-get remove -y python-pip git
    rm -rf /var/lib/apt/lists/*
