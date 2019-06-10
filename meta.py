import os
import argparse


#Read GDC sample sheet (With header)
def readGDC(filename, header = True):
    with open(filename, 'r') as f:
        if header:
            f.readline()
        for i in f:
            print(i)
            getSVS(i[1].strip())

#Get SVS from gcloud
def getSVS(fname, bucket = 'nci-test'):
    cmd = "singularity run --app download gcloud.sif -f %s -b %s" % (fname, bucket)
    os.system(cmd)
            
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
