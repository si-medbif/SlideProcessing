#!/usr/bin/env python

import argparse
from google.cloud import storage
import os
from joblib import Parallel, delayed
import itertools

def list_blobs_with_prefix(bucket_name, prefix, delimiter=None):
    """Lists all the blobs in the bucket that begin with the prefix.
    This can be used to list all blobs in a "folder", e.g. "public/".
    The delimiter argument can be used to restrict the results to only the
    "files" in the given "folder". Without the delimiter, the entire tree under
    the prefix is returned. For example, given these blobs:
        /a/1.txt
        /a/b/2.txt
    If you just specify prefix = '/a', you'll get back:
        /a/1.txt
        /a/b/2.txt
    However, if you specify prefix='/a' and delimiter='/', you'll get back:
        /a/1.txt
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
    result = []
    for blob in blobs:
        result.append(blob.name)
    return(result)

def cmd_prepare(bucket,target):
    cmd = "singularity run --app download gcloud.sif -b %s -f %s -d %s && tar -xzf %s && rm %s" % (bucket,target,target,target,target)
    return(cmd)

def main(args):
    lst = list_blobs_with_prefix(args.bucket,args.folder)
    cmd_list = map(cmd_prepare,itertools.repeat(args.bucket, len(lst)), lst )
    
    Parallel(n_jobs=-1, verbose=1, backend="threading")(map(delayed(os.system), cmd_list))


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-f",
        "--folder",
        action="store",
        help="Name of folder to be downloaded"
    )
    
    parser.add_argument(
        "-b",
        "--bucket",
        action="store",
        help="Name of the bucket"
    )
    
    args = parser.parse_args()
    main(args)
