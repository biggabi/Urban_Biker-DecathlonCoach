#!/usr/bin/python
from __future__ import print_function

import sys, getopt, os

from Urban_Biker_data_parser import find_UB_input_files_in_input_dir, parse_GPX_data, parse_HR_data, create_DecathlonCoach_gpx_file


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

    gpx_track_list = parse_GPX_data(inputfiles['GPX'])
    print('Lenght of GPX track list:', len(gpx_track_list))
    print("gpx_track_list[0]",gpx_track_list[0])
    print("gpx_track_list[1]",gpx_track_list[1])
    print('----')

    HR_list = parse_HR_data(inputfiles['HR'])
    print('Lenght of HR data list:', len(HR_list))
    print('----')

    create_DecathlonCoach_gpx_file(gpx_track_list, HR_list, inputdir, outputdir)

if __name__ == "__main__":
    main(sys.argv[1:])
