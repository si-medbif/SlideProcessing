import os
import argparse
#from joblib import Parallel, delayed
import re
#import random

def list_chkpt(checkpoint_dir):
    result = []
    abdir = os.path.abspath(checkpoint_dir)
    if not os.path.isfile(f'''{abdir}/checkpoint'''):
        return
    with open(f'''{abdir}/checkpoint''', 'r') as f:
        for line in f:
            result.append(line.rstrip())
    return(result[1:])

def tmp_chkpt(chkpt,checkpoint_dir,output_dir):
    abdir = os.path.abspath(output_dir)
    tmpdir = f'''{abdir}/tmp'''
    tmpfile = tmpdir+"/checkpoint"
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    new_chkpt = chkpt.replace(os.path.abspath(checkpoint_dir),tmpdir)
    with open(tmpfile,'w') as f:
        f.write(new_chkpt.replace('all_model_checkpoint_paths','model_checkpoint_path') + "\n")
        f.write(new_chkpt)
    pattern = r'"([A-Za-z0-9_\./\\-]*)"'
    m = re.search(pattern, chkpt)
    chk = m.group(1).replace(os.path.abspath(checkpoint_dir)+"/",'')
    files = [f for f in os.listdir(os.path.abspath(checkpoint_dir)) if re.match(chk, f)]
    for f in files:
        os.symlink(os.path.abspath(checkpoint_dir)+"/"+f,tmpdir+"/"+f)
    chk_dir = abdir+"/"+chk
    if not os.path.exists(chk_dir):
        os.makedirs(chk_dir)
    return(chk_dir)

def run_eval(tmp_dir,chk_dir,data_dir,label_file,type_eval,batch_size):
    cmd = f"""python3 DeepPATH/DeepPATH_code/02_testing/xClasses/nc_imagenet_eval.py --checkpoint_dir='{os.path.abspath(tmp_dir)}' --eval_dir='{os.path.abspath(chk_dir)}' --data_dir='{os.path.abspath(data_dir)}'  --batch_size={batch_size}  --run_once --ImageSet_basename={type_eval} --ClassNumber=2 --mode='0_softmax'  --TVmode='test'"""
    os.system(cmd)
    cmd2 = f"""python3 DeepPATH/DeepPATH_code/03_postprocessing/0h_ROC_MultiOutput_BootStrap.py --file_stats='{os.path.abspath(chk_dir)}/out_filename_Stats.txt' --output_dir='{os.path.abspath(chk_dir)}' --labels_names='{os.path.abspath(label_file)}'"""
    os.system(cmd2)
    os.system(f'''rm {os.path.abspath(tmp_dir)}/*''')

def main(args):
    if args.type_eval not in ['test_','valid_','train_']:
        print("type_eval must be test_','valid_' or 'train_'.")
        return
    lst = list_chkpt(args.checkpoint_dir)
    t = tmp_chkpt(lst[0],args.checkpoint_dir,args.output_dir)
    run_eval(args.output_dir+"/tmp",t,args.data_dir,args.type_eval)
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-c",
        "--checkpoint_dir",
        action="store",
        help="Name and path of the model checkpoints"
    )
    
    parser.add_argument(
        "-o",
        "--output_dir",
        action="store",
        help="Name and path for saving evaluation results"
    )
    
    parser.add_argument(
        "-d",
        "--data_dir",
        action="store",
        help="Name and path of the validate/test TFRecords"
    )
    
    parser.add_argument(
        "-l",
        "--label_file",
        action="store",
        help="Name and path to the label file"
    )
    
    parser.add_argument(
        "-t",
        "--type_eval",
        action="store",
        help="Type of dataset for evaluation ('test_','valid_','train_')"
    )
    
    parser.add_argument(
        "-b",
        "--batch_size",
        action="store",
        default = 20,
        help="Batch size for evaluation"
    )
    
    
    args = parser.parse_args()
    main(args)
