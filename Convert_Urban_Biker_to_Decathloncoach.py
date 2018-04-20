#!/usr/bin/python
from __future__ import print_function

import sys, getopt, os

from Urban_Biker_data_parser import find_urban_biker_input_files_in_input_dir, parse_gpx_data, parse_hr_data, create_decathloncoach_gpx_file


def main(argv):
    inputdir = ''
    outputdir = ''
    split = False
    decreased_granularity = False
    cadence_swap_vs_heart_rate = False
    try:
        opts, args = getopt.getopt(argv,"cdhsi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('Convert_Urban_Biker_to_Decathloncoach.py -i <directory of input files> -o <directory of output files> -d -c')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Convert_Urban_Biker_to_Decathloncoach.py -i <directory of input files> -o <directory of output files> -d -c')
            sys.exit()
        elif opt in ("-d"):
            decreased_granularity = True
        elif opt in ("-s"):
            split = True
        elif opt in ("-c"):
            cadence_swap_vs_heart_rate = True
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

    inputfiles = find_urban_biker_input_files_in_input_dir(inputdir, cadence_swap_vs_heart_rate)
    print('----')
    print('GPX input file: ', inputfiles['GPX'])
    print('HR input file: ', inputfiles['HR'])
    print('Cadence input file: ', inputfiles['CAD'])
    print('Speed input file: ', inputfiles['speed'])
    print('Altitude input file: ', inputfiles['altitude'])
    print('----')

    gpxtracklist = parse_gpx_data(inputfiles['GPX'])
    print('Lenght of GPX track list:', len(gpxtracklist))
    print('----')

    if cadence_swap_vs_heart_rate == False:
        if inputfiles['HR'] == '':
            hrlist = []
        else:
            hrlist = parse_hr_data(inputfiles['HR'])
    else:
        hrlist = parse_hr_data(inputfiles['CAD'])
    print('Lenght of HR data list:', len(hrlist))
    print('----')

    create_decathloncoach_gpx_file(gpxtracklist, hrlist, inputdir, outputdir, split, decreased_granularity, cadence_swap_vs_heart_rate)

if __name__ == "__main__":
    main(sys.argv[1:])
