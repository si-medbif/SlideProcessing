singularity run DeepPATHv4.sif python /opt/DeepPATH/DeepPATH_code/00_preprocessing/TFRecord_2or3_Classes/build_image_data.py --directory='Sorted' --output_directory='TFRecords' --train_shards=1024  --validation_shards=128 --num_threads=8