import os, sys, argparse, random, math, re

def getList(args, header = True):
	result = {}
	with open(os.path.realpath(args.LabelFile), 'r') as f:
		if header:
			next(f,None)
		for line in f:
			l = line.rstrip().split(",")
			pat,old,new,dx,note,date = l[:6]
			if dx not in result.keys():
				result[dx] = []
			result[dx].append(new)
		return result

def sortGroup(result,args):
	sorted_result = {}
	for dx in result.keys():
		sorted_result[dx] = sortList(result[dx],args)
	return sorted_result


def sortList(lst,args):
	slst = {}

	#Train = 0, Test = 1, Validate = 2
	n = len(lst)
	ntest = math.ceil(n * args.PercentTest/100)
	nval = math.ceil(n * args.PercentValid/100)
	indx = [1 for i in range(ntest)]
	indx += [2 for i in range(nval)]
	indx += [0 for i in range(n - (ntest + nval))]
	rindx = random.sample(indx, len(indx))
	rindx_test = [i for i,v in enumerate(rindx) if v == 1] 
	rindx_val = [i for i,v in enumerate(rindx) if v == 2]
	rindx_train = [i for i,v in enumerate(rindx) if v == 0]
	slst["train"] = [v for i,v in enumerate(lst) if i in rindx_train]
	slst["test"] = [v for i,v in enumerate(lst) if i in rindx_test]
	slst["valid"] = [v for i,v in enumerate(lst) if i in rindx_val]
	return slst

def getDxAndType(slst,svsname):
	for dx in slst.keys():
		t_slst = slst[dx]
		result = [key for key,value in t_slst.items() if svsname in value ]
		if len(result) != 0:
			return [dx,result[0]]
	return False

def OldFileNameList(slst,args):
	#reults = []
	flist = os.walk(args.InputFolder)
	for smth in flist:
		m = re.match(".*/(.*?)_files/"+args.Magnification+"$",smth[0])
		if m:
			subdir = m.group(1)
			svsname = subdir + ".svs"
			dx_type = getDxAndType(slst,svsname)
			#print(dx_type)
			if dx_type:
				for member in smth[-1]:
					new_path = os.path.realpath(args.OutputFolder) +"/"+dx_type[0]+"/"
					if not os.path.isdir(new_path):
						os.system("mkdir "+ new_path)

					new_path_file = new_path+dx_type[1]+"_"+subdir+"_"+member
					
					old_path_file = (os.path.realpath(smth[0]) + "/"+member)

					cpcmd = "cp "+old_path_file+" "+new_path_file
					print(cpcmd)
					os.system(cpcmd)


def main(args):
	lst = getList(args)

	if args.Seed != -1:
		random.seed(args.Seed)

	slst = sortGroup(lst,args)
	

	OldFileNameList(slst,args)


if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()

	parser.add_argument(
		"-i",
		"--InputFolder", 
		help="path to tiled images", 
		dest='InputFolder')
	parser.add_argument(
		"-o",
		"--OutputFolder", 
		help="path to save sorted tiled images", 
		dest='OutputFolder')

	parser.add_argument(
    	"-l",
    	"--LabelFile",
    	help="Label file of SVS files", 
    	dest='LabelFile')
	parser.add_argument(
    	"-m",
    	"--Magnification", 
    	help="magnification to use", 
    	type=str, 
    	dest='Magnification')
	parser.add_argument(
    	"-v",
    	"--PercentValid", 
    	help="percentage of images for validation (between 0 and 100)", 
    	type=float,
        dest='PercentValid')
	parser.add_argument("-t",
    	"--PercentTest", 
    	help="percentage of images for testing (between 0 and 100)", 
    	type=float,
        dest='PercentTest')
	parser.add_argument("-s",
    	"--Seed", 
    	help="Seed number for randomization", 
    	type=int,
    	default=-1,
        dest='Seed')
	
	args = parser.parse_args()
	main(args)

