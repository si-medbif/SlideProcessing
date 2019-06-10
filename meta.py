import os
import argparse


#Read GDC sample sheet (With header)
def readGDC(filename, header = True):
    with open(filename, 'r') as f:
        if header:
            f.readline()
        for line in f:
            lst = line.rstrip().split('\t')
            getSVS(line[1].strip())
            tiling(line[1].strip())

#Get SVS from gcloud
def getSVS(fname, bucket = 'nci-test'):
    cmd = "singularity run --app download gcloud.sif -f %s -b %s" % (fname, bucket)
    print(cmd)
    #os.system(cmd)
def tiling(svs):
    cmd = 'singularity run --app tile DeepPATHv4.sif -s 512 -B 50 -e 0 -j 32 -M 20 -o Results/ "%s"' % svs
    print(cmd)
            
def main(args):
    readGDC(args.file_name)

  
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-f",
        "--file_name",
        action="store",
        help="Name and path of the sample sheet file"
    )
    
    args = parser.parse_args()
    main(args)
