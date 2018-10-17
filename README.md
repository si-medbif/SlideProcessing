# SlideProcessing
Singularity image for preparing file from Asperio (.svs files) for downstream processes (e.g. image processing and machine learning)

---
## Test file
https://sibdm-exome.sgp1.digitaloceanspaces.com/Dumrong/AFB_5081A.svs

---
## Pre-built singularity image

### Singularity 2.x
https://sibdm-exome.sgp1.digitaloceanspaces.com/Dumrong/DeepPATH.simg

---
## How to build Singularity image for DeepPATH

Download the 'Singularity' file from si-medbif/SlideProcessing first

### Singularity 2.x

```shell
$ singularity build DeepPATH.simg Singularity
```
### Singularity 3.x
```shell
$ cp Singularity DeepPATH.def #Create a defition file identical to 'Singularity' file
$ singularity build DeepPATH.sif DeepPATH.def
```
---
## How to use the image

### 0.1 Tile the svs slide images

To process the svs images, go to the parent directory where the slide images or their folder located first. 
In the example below, the slide images are in 'Data/' directory and the output images will be save in 'Results' directory. Both directories are in the current working director (i.e. $PWD).

```shell
$ singularity run -B $PWD --app tile DeepPATH.simg -s 299 -B 25 -e 0 -j 50 -o Results/ "Data/*.svs"
```
Help/Manual for 'tile' app
```shell
$ singularity help --app tile DeepPATH.simg 
```
