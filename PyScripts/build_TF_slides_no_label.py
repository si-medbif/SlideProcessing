from absl import flags
from absl import app
from joblib import Parallel, delayed
import os
import re
import tensorflow as tf
from PIL import Image
import numpy as np

 
# Assign flags
FLAGS = flags.FLAGS
flags.DEFINE_string("source_dir", None, "Path to the parent directory containing subdirectories of tile files processed by VIPS (e.g. /Path/to/<SlideName/level/tile.jpeg>. Not directly to tile files.")
flags.DEFINE_string("out_dir", None, "Path for saving TFRecord files.")
flags.DEFINE_integer("jobs", -1, "Number of threads for parallel processing (default = -1 which means all CPUs will be used).")

# Required flags
flags.mark_flag_as_required("source_dir")
flags.mark_flag_as_required("out_dir")


def _bytes_feature(value):
  """Returns a bytes_list from a string / byte."""
  if isinstance(value, type(tf.constant(0))):
    value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value):
  """Returns a float_list from a float / double."""
  return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
  """Returns an int64_list from a bool / enum / int / uint."""
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def serialize_example(filepath, filename, label, label_index_list):
  image_string = open(filepath, 'rb').read()
  #image_shape = tf.image.decode_jpeg(image_string).shape
  """
  Creates a tf.Example message ready to be written to a file.
  """
  # Create a dictionary mapping the feature name to the tf.Example-compatible
  # data type.
  feature = {
      'image/filename': _bytes_feature(filename.encode('utf-8')),
      'image/encoded':  _bytes_feature(image_string),
      'image/class/label': _int64_feature(label_index_list.index(label)),
      'image/class/text': _bytes_feature(label.encode('utf-8'))
  }
  # Create a Features message using tf.train.Example.
  example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
  return example_proto.SerializeToString()

def TFRecord_writer(slide_name, file_list, out_dir):
  new_filename = os.path.join(out_dir,"%s.tfrecord" % slide_name)
  with tf.io.TFRecordWriter(new_filename) as writer:
    for tile_path, tile_name in file_list:
      example = serialize_example(tile_path,tile_name,"Benign",["Background","CA","Benign"])
      writer.write(example)
  print("%s.tfrecord is completely written with %d tiles" % (slide_name,len(file_list)))

def prep_files(source_dir):
  results = {}
  for r,d,f in os.walk(source_dir):
    for name in f: 
      if "jpeg" in name:
        
        slide_name = r.split("/")[-3]
        tile_name = slide_name + "_" + name 
        tile_path = os.path.join(os.path.abspath(r),name)
        if slide_name in results.keys():
          results[slide_name].append((tile_path,tile_name))
        else:
          results[slide_name] = [(tile_path,tile_name)]
  return results

def main(argv):
  del argv  # Unused.
  
  results = prep_files(FLAGS.source_dir)
  #inputs = [(slide_name, results[slide_name],FLAGS.out_dir) for slide_name in results.keys()]
  #files = set([r.split("/")[1] for r,d,f in os.walk(FLAGS.source_dir) for name in f if "jpeg" in name])
  #files = [(os.path.join(os.path.abspath(r),file),r.split("/")[1],r.split("/")[1]+"_"+file) for r,d,f in os.walk(FLAGS.source_dir) for file in f if "jpeg" in file]
  #print(inputs)
  #dir_list = [os.path.join(FLAGS.source_dir,name) for name in os.listdir(FLAGS.source_dir) if os.path.isdir(os.path.join(FLAGS.source_dir,name))]

  #for r,d,f in os.walk(FLAGS.source_dir):
  #  for name in d:
  #    print(d)

  #TFRecord_writer(FLAGS.source_dir, FLAGS.out_dir,FLAGS.mag,FLAGS.bg_cut)

  #s1 = Slide_Processor(FLAGS.source_dir)
  #print(s1.labels)
  #print(len(s1.raw_path))

  #inputs = [(dir_name,FLAGS.out_dir,FLAGS.mag,FLAGS.bg_cut) for dir_name in dir_list]
  #print(inputs)
  #for dir_name in dir_list:
  #  print(dir_name)
  #  print(select_folder(dir_name,FLAGS.mag))
  Parallel(n_jobs=FLAGS.jobs)(delayed(TFRecord_writer)(slide_name, results[slide_name],FLAGS.out_dir) for slide_name in results.keys())
  #Parallel(n_jobs=FLAGS.jobs)(delayed(TFRecord_writer)(dir_name, FLAGS.out_dir, FLAGS.mag, FLAGS.bg_cut) for dir_name in dir_list)
  
if __name__ == '__main__':
  app.run(main)
