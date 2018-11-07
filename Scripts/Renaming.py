import os, sys, argparse

def getFiles(path_to_file):
    ulist = os.walk(path_to_file)
    return [files for  path, subdirs, files in ulist][-1]

def mvCmd(old,new):
    os.system("mv "+old+" "+new)
    
def cpCmd(old,new):
    os.system("cp -r "+old+" "+new)
    
def main(args):
    with open(os.path.realpath(args.listfile), 'r') as f:
        for line in f:
            l = line.rstrip().split(",")
            pat,old,new,dx,note,date = l[:6]
            if old in getFiles(args.inpath):
                ppath = os.path.abspath(args.inpath)+"/"+pat+"/"
                pdpath = os.path.abspath(args.outpath) + "/"+pat+"/"
                if not os.path.isdir(pdpath):
                    os.system("mkdir "+pdpath)
                cpCmd(ppath+'"'+old+'"', pdpath+new)

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

