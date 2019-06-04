# SlideProcessing
Singularity image for preparing file from Asperio (.svs files) for downstream processes (e.g. image processing and machine learning)

---
## Test file
https://sibdm-exome.sgp1.digitaloceanspaces.com/Dumrong/AFB_5081A.svs

---
## How to build Singularity image for DeepPATH

### Pre-requisite
1. Download the 'DeepPATH.def' file from si-medbif/SlideProcessing
2. Get `libcudnn7-dev_7.6.0.64-1+cuda10.0_amd64.deb`, `libcudnn7-doc_7.6.0.64-1+cuda10.0_amd64.deb` and `libcudnn7_7.6.0.64-1+cuda10.0_amd64.deb` from [NVIDIA](https://developer.nvidia.com/rdp/form/cudnn-download-survey) (NVIDIA account is required).
3. Put 'DeepPATH.def' and libcudnn files in the build directory

### Singularity 3.x
Build a writable image and manually install cuda 10.0 (You will need to enter language and keyboard options so installation by Singularity defintion file is not yet possible).
```shell
$ sudo singularity build --sandbox DeepPATH/ DeepPATH.def && sudo singularity run --writable DeepPATH/ apt install -y cuda-10- && sudo singularity run --writable DeepPATH/ rm -rf /var/lib/apt/lists/*
```

(Optional) Convert an image to a sif file (a single file image). Exit and run this command in the build directory
```shell
$ sudo singularity build DeepPATH.sif DeepPATH/
```

---
## How to use the image

### 0.1 Tile the svs slide images

To process the svs images, go to the parent directory where the slide images or their folder located first. 

In the example below, the slide images are in 'Data/' directory and the output images will be save in 'Results/' directory. Both directories are in the current working directory (i.e. $PWD).

```shell
$ singularity run -B $PWD --app tile DeepPATH.simg -s 299 -B 25 -e 0 -j 50 -o Results/ "Data/*.svs"
```
Help/Manual for 'tile' app
```shell
$ singularity help --app tile DeepPATH.simg 
```
