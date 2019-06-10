import os
import argparse


#Read GDC sample sheet (With header)
def readGDC(filename, header = True):
    with open(filename, 'r') as f:
        if header:
            f.readline()
        for line in f:
            lst = line.rstrip().split('\t')
            fname = lst[1].strip()
            path = fname.replace('.svs','_files')
            getSVS(fname)
            tiling(fname)
            rotate_all(path)

#Get SVS from gcloud
def getSVS(fname, bucket = 'nci-test'):
    cmd = "singularity run --app download gcloud.sif -f %s -b %s" % (fname, bucket)
    print(cmd)
    os.system(cmd)
    
#Tiling SVS file    
def tiling(svs):
    cmd = 'singularity run --app tile DeepPATHv4.sif -s 512 -B 50 -e 0 -j 32 -M 20 -o Results/ "%s"' % svs
    print(cmd)
    os.system(cmd)

#Rotate tile files
def rotate_all(path):
    rotate_dict ={
        1:"FH_",
        2:"FV_",
        3:"R90_",
        4:"R180_",
        5:"R270_"
    }
    for i in rotate_dict.values():
        if not os.path.exists("Results/"+ i+path):
            os.makedirs("Results/"+i+path+"/20.0/")
            
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jpeg"):
                fl = os.path.join(root, file)
                for j in range(1,6):
                    npath = "Results/" + rotate_dict.get(j) + path +"/20.0/"
                    cmd = 'singularity run --app flip DeepPATHv4.sif -i %s -o %s -s %s' % (fl,j,npath)
                    print(cmd)
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
