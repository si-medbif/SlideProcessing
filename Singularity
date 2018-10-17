Bootstrap: docker
From: ubuntu:18.04

%help
    Singularity image for DeepPATH
    

%labels
MAINTAINER dumrong.mai@biotec.or.th
VERSION v0.2
ORIGINAL_SOURCE https://github.com/ncoudray/DeepPATH

%post
    apt-get update && apt-get install -y --no-install-recommends \
            python-dev python-pip git openslide-tools \
            build-essential python-setuptools

    pip install numpy 
    pip install scipy 
    pip install wheel 
    pip install dicom 
    pip install openslide-python

    # Get DeepPATH scripts
    cd /opt && git clone https://github.com/si-medbif/DeepPATH.git
    apt-get remove -y python-pip git
    rm -rf /var/lib/apt/lists/*

# =======================
# 0.1 Tile the svs slide images
# =======================

%appenv tile
    TILE_PY=/opt/DeepPATH/DeepPATH_code/00_preprocessing/0b_tileLoop_deepzoom4.py
    export TILE_PY

%apphelp tile
    Mandatory parameters:
        -s is tile_size: 299 (299x299 pixel tiles)
        -e is overlap, 0 (no overlap between adjacent tiles). Important: the overlap is defined as "the number of extra pixels to add to each interior edge of a tile". Which means that the final tile size is s + 2.e. So to get a 299px tile with a 50% overlap, you need to set s to 149 and e to 75. Also, tile from the edges of the slide will be smaller (since up to two sides have no "interior" edge)
        -j is number of threads: 32 (for a full GPU node on gpu0.q)
        -B is Max Percentage of Background allowed: 25% (tiles removed if background percentage above this value)
        -o is the path were the output images must be saved
        The final mandatory parameter is the path to all svs images. 
        
    Optional parameters when regions have been selected with Aperio:
        -x is the path to the xml files. The rootname of the xml file must match exactly the one of the svs images. All the xml files sharing the same label should be in the same folder (named after this label, for example xml_). If there are ROIs with different labels, they should be saved in separate folders and tiles independently in separate output folders (also named after the label, for example <###>pxTiles_)
        -m 1 or 0 if you want to tile the region inside the ROI, or outside
        -R minimum percentage of tile covered by ROI. If below the percentage, tile is not kept.
        -l To be used with xml file - Only do the tiling for the labels which name contains the characters in this option (string)
        -S Set it to true if you want to save ALL masks for ALL tiles (will be saved in same directory with suffix!!)
    
    Notes:
        This code can also be used to tile input jpg images: the full path to input images will end in <*jpg">, and you need to set the option -x to the '.jpg' string value and -R to the magnification at which the images were acquired (20.0 for example)
        known bug: the library used fails to deal with images compressed as JPG 2000. These would lead to empty directories
        Output:

        Each slide will have its own folder and inside, one sub-folder per magnification. Inside each magnification folder, tiles are named according to their position within the slide: <x>_<y>.jpeg.
        If the extraction is made from masks defined in xml files, the tiles slides will be saved in folders named after the label of the layer (version 3 of the code only).

%apprun tile
    python $TILE_PY "$@"