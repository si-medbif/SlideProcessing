#For sorted and rotate file 


import os, sys, argparse
#from joblib import Parallel, delayed
import re
import random

def cp_list(fname,inpath,outpath,label,group):
    lst = []
    path = os.path.abspath(inpath)+"/"+ fname.rstrip("_files")+"_files" 
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ff in filenames:
            cmd = "cp " + dirpath+"/"+ff + " " + os.path.abspath(outpath)+"/"+label.strip()+"/"+group.strip()+fname+"_"+ff
            lst.append(cmd)
    return(lst)

def rotate_list(fname,inpath,outpath,label,group,nrotate):
    #print(fname,inpath,outpath,label,group,nrotate)
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
    path = os.path.abspath(inpath)+"/"+ fname.rstrip("_files")+"_files" 
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ff in filenames:
            for j in random.sample(rotate_dict.keys(),int(nrotate)-1):
                fl = dirpath+"/"+ff
                npath = os.path.abspath(outpath)+"/"+label.strip()+"/"+group.strip()+rotate_dict.get(j)+fname+"_"+ff
                cmd = 'singularity run --app flip DeepPATHv4.sif -i %s -o %s -s %s' % (fl,j,npath)
                lst.append(cmd)
    return(lst)

def getOriFiles(path_to_file):
    ulist = os.walk(path_to_file)
    return [ os.path.join(path,f) for path, subdirs, files in ulist for f in files]

def getFiles(path_to_file):
    ulist = os.walk(path_to_file)
    return [files for  path, subdirs, files in ulist][-1]

def main(args):
    with open(os.path.realpath(args.listfile), 'r') as f:
        for line in f:
            l = line.rstrip().split(",")
            fname,label,group,nrotate = l

            print(fname)
            
            CP = cp_list(fname,args.inpath,args.outpath,label,group)
            for cmd in CP:
            	os.system(cmd)
            print("Copy complete")
            ROTATE = rotate_list(fname,args.inpath,args.outpath,label,group,nrotate)
            if len(ROTATE) > 0:
            	for cmd in ROTATE:
            		os.system(cmd)
            print("Rotate complete")

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument(
        "-l",
        "--listfile",
        action="store",
        help="Path and file name of a list of files to be renamed"
    )
    
    parser.add_argument(
        "-i",
        "--inpath",
        action="store",
        help="Path to original files"
    )
    
    parser.add_argument(
        "-o",
        "--outpath",
        action="store",
        help="Path for renamed files "
    )
    
    args = parser.parse_args()
    main(args)
