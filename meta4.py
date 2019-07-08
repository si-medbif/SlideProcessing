import os
import argparse
from joblib import Parallel, delayed
import re

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
            
            if re.search("normal",lst[7],re.IGNORECASE):
                cmd_list = rotate_all_prep(path)
                Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), cmd_list))
            
            cmd_list,cmd_list2 = tar_gz_prep(path)
            
            Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), cmd_list))
            

            Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), cmd_list2))
            
            os.system("rm -rf ~/Results")
            os.system("rm " + fname)

#Get SVS from gcloud
def getSVS(fname, bucket = 'nci-test'):
    cmd = "singularity run --app download gcloud.sif -f %s -b %s" % (fname, bucket)

    os.system(cmd)
    
#Tiling SVS file    
def tiling(svs):
    cmd = 'singularity run --app tile DeepPATHv4.sif -s 512 -B 50 -e 0 -j 32 -M 20 -o Results/ "%s"' % svs

    os.system(cmd)

#Rotate tile files commands
def rotate_all_prep(path):
    cmd_list = []
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
            
    for root, dirs, files in os.walk("Results/" + path):
        for file in files:
            #print(file)
            if file.endswith(".jpeg"):
                fl = os.path.join(root, file)
                for j in range(1,6):
                    npath = "Results/" + rotate_dict.get(j) + path +"/20.0/"
                    cmd = 'singularity run --app flip DeepPATHv4.sif -i %s -o %s -s %s' % (fl,j,npath + file)
                    cmd_list.append(cmd)
    return(cmd_list)

#Create compressed files commands
def tar_gz_prep(path):
    cmd_list = []
    cmd_list2 = []
    npath = path.rstrip("/")
    lst = os.listdir("Results")
    for l in lst:
        if npath in l and "dzi" not in l:
            cmd = "tar -czf Results/%s.tar.gz Results/%s/" % (l, l)
            cmd_list.append(cmd)
            cmd2 = "singularity run --app upload gcloud.sif -b nci-test -c Results/%s.tar.gz -d tiles/"  %  l
            cmd_list2.append(cmd2)

    return(cmd_list, cmd_list2)

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
