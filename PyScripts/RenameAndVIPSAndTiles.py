import os
import shutil
from datetime import datetime
import json
import re
import string
import random
from absl import app
from absl import flags

# Assign flags
FLAGS = flags.FLAGS
flags.DEFINE_string("source_dir", None, "Path to Raw slide files (e.g. *.svs, *.mrxs).")
flags.DEFINE_string("dzi_dir", None, "Path for saving DZI files.")
flags.DEFINE_string("tile_dir", None, "Path for saving tile files.")
flags.DEFINE_string("log_file", None, "Path to a json log file.")
flags.DEFINE_string("failed_log_file", None, "Path to a json log file for errors.")
flags.DEFINE_boolean('ano', False, 'Anonymize names of files. Should be used if names contain identifier like HN or AN.')
flags.DEFINE_integer('tile_size', 299, 'Tile size in pixels.', lower_bound=1, upper_bound =8192)
flags.DEFINE_integer('overlap', 0, 'Tile overlap in pixels.', lower_bound=0, upper_bound =8192)
flags.DEFINE_enum("mag", "10",["5","10","20","40"], "Magnification levels to be saved (default = 10x).")
flags.DEFINE_integer('jobs', 6, 'Parallel threading for tiling process (defult = 1)')
flags.DEFINE_integer("bg_cut",50,"If percent of background in a tile >= 'bg_cut' (in %), the tile will be labelled as a background (default = 50%).")



# Required flags
flags.mark_flag_as_required("source_dir")
flags.mark_flag_as_required("dzi_dir")
flags.mark_flag_as_required("tile_dir")
flags.mark_flag_as_required("log_file")
flags.mark_flag_as_required("failed_log_file")

VIPS_SING = "libvips-openslide-alpine.sif" #Path to VIPS singularity container
TILE_SING = "DeepPATHv4.sif" #Path to Tiling (DeepPATH) singularity container

def random_string(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase + string.ascii_uppercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def get_ext(name):
	"""Extract file extension"""
	m = re.match(".+(\..+)$",name)
	if m:
		return m.group(1)
	else:
		return ".ERROR"

def rid_ext(name):
	"""Eliminate file extension"""
	m = re.match("(.+)(\..+)$",name)
	if m:
		return m.group(1)
	else:
		return m.group(0)

def fix_illegal(name):
	"""Remove illegal characters"""
	new_name = name.replace(" ","_")
	illegal_chars = ["(",")","*"]
	for char in illegal_chars:
		new_name = new_name.replace(char,"")
	return new_name

def prep_cmd(src,dzi_dest,tile_dest,tile_size, overlap, ano, mag, jobs, bg_cut):
	"""Prepare VIPS command for converting large slide images to deepzoom objects (dzi)"""
	vips_cmd = "singularity exec " + VIPS_SING +" vips dzsave "
	#singularity run --app tile DeepPATHv4.sif -s 299 -e 0 -j 32 -B 50 -M 10 -o Prostate_tiles/ -x Prostate_XML/ -m 1 -R 25 -l ''  "Prostate_AJ_CA/*svs"
	tile_cmd = "singularity run --app tile %s -s %d -e %d -j %d -B %d -M %s -o " % (TILE_SING, tile_size, overlap, jobs, bg_cut, mag)
	os.makedirs("tmp", exist_ok = True)
	os.makedirs(dzi_dest, exist_ok = True)
	os.makedirs(tile_dest, exist_ok = True)
	if ano:
		dzi_files = [(r,name,dzi_dest,random_string(),get_ext(name)) for r,d,f in os.walk(src) for name in f if "svs" in name]
	else:
		dzi_files = [(r,name,dzi_dest,rid_ext(fix_illegal(name)),get_ext(fix_illegal(name))) for r,d,f in os.walk(src) for name in f if "svs" in name]
	_ = [os.symlink(os.path.abspath(os.path.join(r_old,f_old)),os.path.join("tmp",f_new+ext_new)) for r_old,f_old,r_new,f_new,ext_new in dzi_files]
	tile_cmd = tile_cmd + '%s "tmp/*svs"' % tile_dest
	vips_cmds = [vips_cmd + "%s %s --tile-size=%d --overlap=%d" % (os.path.join("tmp",f_new+ext_new), os.path.join(r_new,f_new), tile_size, overlap) for r_old,f_old,r_new,f_new,ext_new in dzi_files]
	
	print("Tiling")
	os.system(tile_cmd)

	print("Generating Deep Zoom objects")
	for cmd in vips_cmds:
		print(cmd)
		os.system(cmd)
	#	print(cmd)
	#os.system(tile_cmd)

	shutil.rmtree("tmp")
	logs = [{"original":os.path.join(r_old,f_old), 
			"vips":os.path.join(dzi_dest,f_new + "_files"),
			"tile":os.path.join(tile_dest,f_new + "_files"),
			"status":"DZI and Tiles generated",
			"date_modified":str(datetime.now())} for r_old,f_old,r_new,f_new,ext_new in dzi_files if os.path.exists(os.path.join(dzi_dest,f_new + "_files")) and os.path.exists(os.path.join(tile_dest,f_new + "_files"))]
	
	failed_logs = [{"original":os.path.join(r_old,f_old), 
			"vips":os.path.join(dzi_dest,f_new + "_files"),
			"tile":os.path.join(tile_dest,f_new + "_files"),
			"status":"DZI and/or Tiles failed to be generated",
			"date_modified":str(datetime.now())} for r_old,f_old,r_new,f_new,ext_new in dzi_files if not (os.path.exists(os.path.join(dzi_dest,f_new + "_files")) and os.path.exists(os.path.join(tile_dest,f_new + "_files")))]
	

	return logs, failed_logs

def main(argv):
	del argv #Unused
	logs, failed_logs = prep_cmd(FLAGS.source_dir,FLAGS.dzi_dir,FLAGS.tile_dir,FLAGS.tile_size, FLAGS.overlap, FLAGS.ano, FLAGS.mag, FLAGS.jobs, FLAGS.bg_cut)
	with open(FLAGS.log_file,'w') as outfile:
		for dic in logs:
			json.dump(dic, outfile)
			outfile.write("\n")

	if len(failed_logs) > 0:
		with open(FLAGS.failed_log_file,'w') as outfile:
			for dic in failed_logs:
				json.dump(dic, outfile)
				outfile.write("\n")
	#print(logs)

if __name__ == '__main__':
	app.run(main)
