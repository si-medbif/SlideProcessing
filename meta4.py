import os
import argparse
from joblib import Parallel, delayed
import re

#Read GDC sample sheet (With header)
def readGDC(filename, inpath, outpath, header = True):
    with open(filename, 'r') as f:
        if header:
            f.readline()
        for line in f:
            lst = line.rstrip().split('\t')
            fname = lst[0].strip()
            path = os.path.abspath(inpath)+"/"+ fname+"_files" 
            
            CP = (cp_list(fname,inpath,outpath,lst[1],lst[2]))
            ROTATE = (rotate_list(fname,inpath,outpath,lst[1],lst[2],lst[3]))
            Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), CP))
            Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), ROTATE))
            
def cp_list(fname,inpath,outpath,label,group):
    lst = []
    path = os.path.abspath(inpath)+"/"+ fname+"_files" 
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ff in filenames:
            cmd = "cp " + dirpath+"/"+ff + " " + os.path.abspath(outpath)+"/"+label.strip()+"/"+group.strip()+fname+"_"+ff
            lst.append(cmd)
    return(lst)

def rotate_list(fname,inpath,outpath,label,group,nrotate):
    lst = []
    rotate_dict ={
        1:"FH_",
        2:"FV_",
        3:"R90_",
        4:"R180_",
        5:"R270_"
    }
    if int(nrotate) <= 1:
        return(lst)
    path = os.path.abspath(inpath)+"/"+ fname+"_files" 
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ff in filenames:
            for j in range(1,int(nrotate)):
                fl = dirpath+"/"+ff
                npath = os.path.abspath(outpath)+"/"+label.strip()+"/"+group.strip()+rotate_dict.get(j)+fname+"_"+ff
                cmd = 'singularity run --app flip DeepPATHv4.sif -i %s -o %s -s %s' % (fl,j,npath)
                lst.append(cmd)
    return(lst)
            
def main(args):
    readGDC(args.file_name, args.input_path, args.output_path, header = False)

  
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-f",
        "--file_name",
        action="store",
        help="Name and path of the sample sheet file"
    )
    
    parser.add_argument(
        "-i",
        "--input_path",
        action="store",
        help="Name and path of the tile files"
    )
    
    parser.add_argument(
        "-o",
        "--output_path",
        action="store",
        help="Name and path of the destinateion for sorted tile files. The destination must have subdirectories of labels (e.g Dest/Label1/ Dest/Label2/"
    )
    
    args = parser.parse_args()
    main(args)
