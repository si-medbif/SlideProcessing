import os
import argparse


#Read GDC sample sheet (With header)
def readGDC(filename, header = True):
    with open(filename, 'r') as f:
        if header:
            f.readline()
        for i in f:
            print(i)

def main(args):
    readGDC(args.file_name)

  
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-f",
        "--file_name",
        action="store",
        help="Name and path of the sample sheet file"
    )
