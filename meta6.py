import glob
import random
import os
import argparse
import itertools

SEED = 191017
SELECT = 4000

def get_files_list(path,keyword = ''):
	abspath = os.path.abspath(path)
	print(abspath)
	return [f for f in glob.glob(abspath + "/"+keyword, recursive=False)]

def sample_files_list(file_list, k, SEED):
	random.seed(SEED)
	return random.sample(file_list, k)

def change_path(newpath,filelist):
	abspath = os.path.abspath(newpath)
	basefilelist = map(os.path.basename,filelist)
	newfilelist = map(os.path.join,itertools.repeat(abspath,len(filelist)), basefilelist)
	return newfilelist

def main(args, SEED, SELECT):
	train_list = get_files_list(args.inpath,"train_*")
	new_train_list = change_path(args.outpath,train_list)
	counter = 0
	for i,j in zip(train_list,new_train_list) :
		os.symlink(i,j)
		counter += 1
	print("train_ files = " + str(counter))

	valid_list = get_files_list(args.inpath,"valid_*")
	ran_valid_list = sample_files_list(valid_list, SELECT, SEED)
	new_ran_valid_list = change_path(args.outpath,ran_valid_list)
	counter = 0
	for i,j in zip(ran_valid_list,new_ran_valid_list) :
		os.symlink(i,j)	
		counter += 1
	print("Random valid_ files = " + str(counter))

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-i",
        "--inpath",
        action="store",
        help="Name and path of the model checkpoints"
    )
    
    parser.add_argument(
        "-o",
        "--outpath",
        action="store",
        help="Name and path for saving evaluation results"
    )
    
    
    args = parser.parse_args()
    main(args, SEED, SELECT)
