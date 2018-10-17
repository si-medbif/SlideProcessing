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
singularity build DeepPATH.simg Singularity
```
### Singularity 3.x
```shell
cp Singularity DeepPATH.def #Create a defition file identical to 'Singularity' file
singularity build DeepPATH.sif DeepPATH.def
```

