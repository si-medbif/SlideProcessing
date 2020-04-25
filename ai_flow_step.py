from absl import flags
from absl import app
import json
import os
from datetime import datetime

# Assign flags
FLAGS = flags.FLAGS
flags.DEFINE_string("source_dir", "Raw_Slides", "Path to Raw slide files (e.g. *.svs, *.mrxs).")
flags.DEFINE_string("dzi_dir", "Slide_Dzi", "Path for saving DZI files.")
flags.DEFINE_string("tile_dir","Slide_Tile", "Path for saving tile files.")
flags.DEFINE_string("logs_dir", "logs/", "Path for saving log files.")
flags.DEFINE_boolean('ano', False, 'Anonymize names of files. Should be used if names contain identifier like HN or AN.')
flags.DEFINE_integer('tile_size', 299, 'Tile size in pixels.', lower_bound=1, upper_bound =8192)
flags.DEFINE_integer('overlap', 0, 'Tile overlap in pixels.', lower_bound=0, upper_bound =8192)
flags.DEFINE_enum("mag", "10",["5","10","20","40"], "Magnification levels to be saved (default = 10).")
flags.DEFINE_integer('jobs', 6, 'Parallel threading for tiling process (defult = 6)')
flags.DEFINE_integer("bg_cut",50,"If percent of background in a tile >= 'bg_cut' (in %), the tile will be labelled as a background (default = 50%).")
flags.DEFINE_string("model_json", "Models/EfficientNetB4_fulltrain/model.json", "Path to json file containing the structure of the model to be tested")
flags.DEFINE_string("chkpt", "Models/EfficientNetB4_fulltrain/weights-improvement-007-0.828.ckpt", "Path to saved weight checkpoint for transfer learning (Imagenet weights if not specified)")
flags.DEFINE_string("tfrec_dir", "Slide_TFRecords", "Path for saving TFRecord files")
flags.DEFINE_integer("batch_size",1,"Batch size (default = 1)")
flags.DEFINE_string("pred_dir", "Slide_Prediction", "Path for saving prediction files")
flags.DEFINE_string("heat_dir", "Slide_Heatmap", "Path for saving heatmap files")
flags.DEFINE_string('cut_off', "0.5", 'Mid-point of prediction scores for classification (default = 0.5)')
flags.DEFINE_integer("slices",10,"Number of colors to be included in the heatmap gradient scale (default = 10)")
flags.DEFINE_integer("width",1000,"Width in pixels of a resized heatmap using in the web application (default = 1000)")
flags.DEFINE_string("complete_dir", "Processed_Slides", "Path for moving processed slide files to")
flags.DEFINE_integer('step', 0, 'Step to start. 0 = Run all steps. 1 = Start at creating TFRecords from tile files. 2 = Start at creating prediction files. 3 = Start at creating heatmaps. (default = 0)', lower_bound=0, upper_bound =3)

def rename_vips_tile(source_dir,dzi_dir,tile_dir,log_dir,tile_size,overlap,mag,jobs,bg_cut,ano):
	svs_list = [name for r,d,f in os.walk(source_dir) for name in f if "svs" in name]
	assert len(svs_list) > 0, "No slide files in the source directory!"
	log_file = os.path.join(log_dir,"tmplog.json")
	failed_log_file = os.path.join(log_dir,"tmpfailed_log_VIPS_Tiles.json")
	cmd = "python3 PyScripts/RenameAndVIPSAndTiles.py --source_dir=%s --dzi_dir=%s --tile_dir=%s --log_file=%s --failed_log_file=%s --tile_size=%d --overlap=%d --mag=%s --jobs=%d --bg_cut=%d" 
	cmd = cmd % (source_dir,dzi_dir,tile_dir,log_file,failed_log_file,tile_size,overlap,mag,jobs,bg_cut)
	if ano:
		cmd += " --ano"
	return cmd

def read_log(log_dir):
	log_file = os.path.join(log_dir,"tmplog.json")
	#print(log_file)
	data = []
	with open(log_file,'r') as f:
		for line in f:
			data.append(json.loads(line))
	return data

def write_log(log_file,logs):
	with open(log_file,'w') as outfile:
		for dic in logs:
			json.dump(dic, outfile)
			outfile.write("\n")

def tfrec(data_dict,tfrec_dir,jobs,log_dir,tile_dir):
	log_file = os.path.join(log_dir,"tmplog.json")
	failed_log_file = os.path.join(log_dir,"tmpfailed_log_tfrec.json")
	cmd = "singularity exec --nv tensorflow-gpu.sif python3 PyScripts/build_TF_slides_no_label.py --source_dir=%s --out_dir=%s --jobs=%d"
	new_data_dict = []
	failed_data_dict = []
	for item in data_dict:
		if os.path.exists(item['tile']): 
			print(cmd % (item['tile'],tfrec_dir,jobs))
			os.system(cmd % (item['tile'],tfrec_dir,jobs))
			item["tfrec"] = item['tile'].replace(tile_dir.rstrip("/"),tfrec_dir.rstrip("/"))+".tfrecord"
			item["status"] = "TFRecord generated" 
			new_data_dict.append(item)
		else:
			item["status"] = "Tile files does not exist" 
			failed_data_dict.append(item)

	write_log(log_file,new_data_dict)
	if len(failed_data_dict) > 0:
		write_log(failed_log_file,failed_data_dict)
	return new_data_dict

def predict(data_dict,pred_dir,model_json,chkpt,batch_size, tile_dir,log_dir):
	log_file = os.path.join(log_dir,"tmplog.json")
	failed_log_file = os.path.join(log_dir,"tmpfailed_log_pred.json")
	cmd = "singularity exec --nv tensorflow-gpu.sif python3 PyScripts/eval_mod_single_file.py --source_file=%s --out_dir=%s --model_json=%s --chkpt=%s --batch_size=%d"
	new_data_dict = []
	failed_data_dict = []
	for item in data_dict:
		if os.path.exists(item['tfrec']):
			print(cmd % (item['tfrec'],pred_dir,model_json,chkpt,batch_size))
			os.system(cmd % (item['tfrec'],pred_dir,model_json,chkpt,batch_size))
			item['pred'] = item['tile'].replace(tile_dir.rstrip("/"),pred_dir.rstrip("/"))+".txt"
			item["status"] = "Prediction generated" 
			new_data_dict.append(item)
		else:
			item["status"] = "TFRecord does not exist" 
			failed_data_dict.append(item)
	write_log(log_file,new_data_dict)
	if len(failed_data_dict) > 0:
		write_log(failed_log_file,failed_data_dict)
	return new_data_dict

def heatmap(data_dict,heat_dir,mag,cut_off,slices,width, tile_dir,log_dir):
	log_file = os.path.join(log_dir,"tmplog.json")
	failed_log_file = os.path.join(log_dir,"tmpfailed_log_heat.json")
	cmd = "singularity exec r-tidyverse-imager.sif Rscript RScripts/HeatMap.R -i %s -v %s -o %s -m %s -c %s -s %d -w %d"
	new_data_dict = []
	failed_data_dict = []
	for item in data_dict:
		if os.path.exists(item['pred']) and os.path.exists(item['vips']):
			print(cmd % (item['pred'],item['vips'],heat_dir,mag,cut_off,slices,width))
			os.system(cmd % (item['pred'],item['vips'],heat_dir,mag,cut_off,slices,width))
			item['heatmap'] = item['tile'].replace(tile_dir.rstrip("/"),os.path.join(heat_dir,"Original").rstrip("/"))+".jpeg"
			item["status"] = "Heatmap generated" 
			new_data_dict.append(item)
		elif os.path.exists(item['pred']):
			item["status"] = "DZI does not exist" 
			failed_data_dict.append(item)
		else:
			item["status"] = "Prediction file does not exist" 
			failed_data_dict.append(item)	
	write_log(log_file,new_data_dict)
	if len(failed_data_dict) > 0:
		write_log(failed_log_file,failed_data_dict)
	return(new_data_dict)

def complete(data_dict, source_dir,complete_dir):
	new_data_dict = []
	for item in data_dict:
		dest = item['original'].replace(source_dir.rstrip("/"),complete_dir.rstrip("/"))
		path,file = os.path.split(dest)
		if not os.path.isdir(path):
			os.mkdir(path)
		os.replace(item['original'], dest)

		opath, ofile = os.path.split(item['original'])
		odir = [name for name in os.listdir(opath) if "svs" in name]
		if len(odir) == 0:
			os.rmdir(opath) 

		item["current"] = dest
		item['status'] = "Complete"
		new_data_dict.append(item)
	return(new_data_dict)

def write_log_final(data_dict,log_dir):
	log_file = os.path.join(log_dir,"log_"+ str(datetime.timestamp(datetime.now()))+".json")
	with open(log_file,'w') as outfile:
		for dic in data_dict:
			json.dump(dic, outfile)
			outfile.write("\n")
def main(argv):
  del argv  # Unused.
  #Step 1 Rename and Vips and Tile
  if FLAGS.step == 0:
  	os.system(rename_vips_tile(FLAGS.source_dir,
  		FLAGS.dzi_dir,
  		FLAGS.tile_dir,
  		FLAGS.logs_dir,
  		FLAGS.tile_size,
  		FLAGS.overlap,
  		FLAGS.mag,
  		FLAGS.jobs,
  		FLAGS.bg_cut,
  		FLAGS.ano))
  
  #Step2 Read log file
  data_dict = read_log(FLAGS.logs_dir)
  
  if FLAGS.step <= 1:
  	
  	#Step3 Create TFRecords
  	print("Creating TFRecords.")
  	data_dict = tfrec(data_dict,FLAGS.tfrec_dir,FLAGS.jobs,FLAGS.logs_dir,FLAGS.tile_dir)
  
  if FLAGS.step <= 2:
  	#Step4 Make a prediction
  	print("Predicting from a pre-trained model.")
  	data_dict = predict(data_dict,FLAGS.pred_dir,FLAGS.model_json,FLAGS.chkpt,FLAGS.batch_size, FLAGS.tile_dir,FLAGS.logs_dir)
  

  #Step5 Make a heatmap
  print("Generating heatmaps from predictions.")
  data_dict = heatmap(data_dict,FLAGS.heat_dir,FLAGS.mag,FLAGS.cut_off,FLAGS.slices,FLAGS.width, FLAGS.tile_dir,FLAGS.logs_dir)
  
  #Step6 Move processed slide file to elsewhere
  print("Finishing...")
  data_dict = complete(data_dict, FLAGS.source_dir,FLAGS.complete_dir)
  #Step7 Write the final log file.
  write_log_final(data_dict,FLAGS.logs_dir)
  print("Finished.")

if __name__ == '__main__':
  app.run(main)
