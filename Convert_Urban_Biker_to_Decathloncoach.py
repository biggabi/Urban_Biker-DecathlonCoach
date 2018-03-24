#!/usr/bin/python
from __future__ import print_function

import sys, getopt, os

from Urban_Biker_data_parser import find_UB_input_files_in_input_dir, parse_GPX_data, parse_HR_data


def main(argv):
    inputdir = ''
    outputdir = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('Convert_Urban_Biker_to_Decathloncoach.py -i <directory of input files> -o <directory of output files>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Convert_Urban_Biker_to_Decathloncoach.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputdir = arg
        elif opt in ("-o", "--ofile"):
            outputdir = arg
    if inputdir == '' or outputdir == '':
        print('ERROR: Both input and output directories need to be defined.')
        sys.exit()

    inputdir = os.path.abspath(inputdir)
    outputdir = os.path.abspath(outputdir)

    print('Input directory is ', inputdir)
    print('Output directory is ', outputdir)
    print('----')

    inputfiles = find_UB_input_files_in_input_dir(inputdir)
    print('----')
    print('GPX input file: ', inputfiles['GPX'])
    print('HR input file: ', inputfiles['HR'])
    print('Speed input file: ', inputfiles['speed'])
    print('Altitude input file: ', inputfiles['altitude'])
    print('----')

    track_list = parse_GPX_data(inputfiles['GPX'])
#    for track in track_list: print(track)
    print('Lenght of track list:', len(track_list))
    print('----')

    HR_list = parse_HR_data(inputfiles['HR'])


if __name__ == "__main__":
    main(sys.argv[1:])
