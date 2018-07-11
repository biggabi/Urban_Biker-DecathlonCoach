from __future__ import print_function

import sys
import re

from os import listdir
from os import remove
from os.path import isfile, join, basename, normpath

from datetime import datetime

from random import randint

import gpxpy.parser as parser

from svgpathtools import svg2paths

from DecathlonCoach_format_gpx_fragments import DECATHLONCOACH_GPX_HEADER, DECATHLONCOACH_GPX_END


def find_urban_biker_input_files_in_input_dir(inputdir, cadence_swap_vs_heart_rate):
    print('Looking for files in input directory: ', inputdir)
    gpxinputfile = ''
    hrinputfile = ''
    cadenceinputfile = ''
    speedinputfile = ''
    altitudeinputfile = ''

    files = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]

    for filename in files:
        gpxinputfile = check_input_filenames(filename, '.gpx', gpxinputfile, 'GPX')
        hrinputfile = check_input_filenames(filename, '_duration-heartrate.svg', hrinputfile, 'HR')
        cadenceinputfile = check_input_filenames(filename, '_duration-cadence.svg', cadenceinputfile, 'CAD')
        speedinputfile = check_input_filenames(filename, '_duration-speed.svg', speedinputfile, 'SPEED')
        altitudeinputfile = check_input_filenames(filename, '_duration-altitude.svg', altitudeinputfile, 'ALTITUDE')

    if gpxinputfile == '':
        print ('ERROR: No GPX file in input directory.')
        sys.exit()
    if cadence_swap_vs_heart_rate == False and hrinputfile == '':
        print ('WARNING: No HR file in input directory. HR data is set to 0.')
    if cadenceinputfile == '':
        print ('ERROR: No cadence file in input directory.')
        sys.exit()
    if altitudeinputfile == '':
        print ('ERROR: No altitude file in input directory.')
        sys.exit()

    inputfiles = {'GPX':concat_inputdir(inputdir,gpxinputfile),
                  'HR':concat_inputdir(inputdir,hrinputfile),
                  'CAD':concat_inputdir(inputdir,cadenceinputfile),
                  'speed':concat_inputdir(inputdir,speedinputfile),
                  'altitude':concat_inputdir(inputdir,altitudeinputfile)}

    return inputfiles

def concat_inputdir(inputdir, inputfile):
    if inputfile == '':
        return inputfile
    return (inputdir+'/'+inputfile)

def check_input_filenames(filename, filenamefragment, inputfile, filetype):
    regextocheck = '[-0-9\.]+' + filenamefragment + '$'
    if re.findall(regextocheck, filename):
        if inputfile == '':
            inputfile = filename
        else:
            print ('ERROR: Multiple', filetype, 'files in input directory.')
            sys.exit()
    return inputfile


def parse_gpx_data(gpx_file_name):
    gpx_file = open(gpx_file_name, 'r')
    gpx_parser = parser.GPXParser( gpx_file )
    gpx = gpx_parser.parse()
    gpx_file.close()

    track_list = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.extensions != {}: speed = point.extensions['gpxtpx:speed']
                else: speed = 0
                track_list.append({'lat':point.latitude, 'lon':point.longitude, 'ele':point.elevation, 'time':point.time, 'speed': speed})

    return track_list


def parse_hr_data(input_hr_file):
    clean_hr_file = input_hr_file + ".tmp"
    create_clean_svg_file(input_hr_file, clean_hr_file)

    paths, attributes = svg2paths(clean_hr_file, False, True, False, False)

    # Delete clean_hr_file
    remove(clean_hr_file)    

    hr_measurement = []

    for hr_measurement_sample in attributes[0]['points'].split():
        hr_measurement.append([float((hr_measurement_sample.split(',')[0])), float(hr_measurement_sample.split(',')[1])])

    return hr_measurement


def create_clean_svg_file(input_hr_file_name, output_hr_file_name):
    # Remove all polyline data sections from svg file that is not 'class="data"' or empty.
    # Let's do it ugly: remove lines with
    #   "\" /><polyline class=\"data\" points=\"" and 
    #   "<polyline class=\"grid\" points=\"" content

    f = open(input_hr_file_name,"r")
    lines = f.readlines()
    f.close()

    f = open(output_hr_file_name,"w")
    regex_for_data = "\" /><polyline class=\"data\" points=\""
    regex_for_grid = "<polyline class=\"grid\" points=\""
    for line in lines:
        if not re.findall(regex_for_data, line) and not re.findall(regex_for_grid, line):
            f.write(line)
    f.close()


def create_decathloncoach_gpx_file(gpxtracklist, hrlist, inputdir, outputdir, split, decreased_granularity, cadence_swap_vs_heart_rate):
    outputfile = outputdir + "/" + basename(normpath(inputdir)) + "_DecathlonCoach_format"
    if cadence_swap_vs_heart_rate == True:
        outputfile = outputfile + "_cadence_hr_swapped"
    outputfile = outputfile + ".gpx"
    f = open(outputfile, "w")

    f.write(DECATHLONCOACH_GPX_HEADER)

    max_difference_between_neighbouring_elevation_samples = 0
    time_of_max_elevation_diff = ""
    max_difference_between_neighbouring_lat_samples = 0
    time_of_max_lat_diff = ""
    max_difference_between_neighbouring_lon_samples = 0
    time_of_max_lon_diff = ""
    max_difference_between_neighbouring_timestamps = 0
    time_of_max_time_diff = ""
    min_difference_between_neighbouring_timestamps = 20
    time_of_min_time_diff = ""
    previous_gpx_track_sample = ""

    max_track_length = 2950 # It worked for 20180610-1

    i = 0
    for gpx_track_sample in gpxtracklist:
        if (decreased_granularity == False or \
            (len(gpxtracklist) <= max_track_length) or
            ( (decreased_granularity == True) and (i&int(len(gpxtracklist)/max_track_length + 1) == 0) ) ):

            f.write("            <trkpt lat=\"" + str("%.5f" % gpx_track_sample["lat"]) + "\" lon=\"" + str("%.5f" % gpx_track_sample["lon"]) + "\">\n")
            f.write("                <ele>"+ str(int(gpx_track_sample["ele"])) +"</ele>\n")
            f.write("                <time>" + str(gpx_track_sample["time"])[0:10] + "T" + str(gpx_track_sample["time"])[11:19] + "Z</time>\n")
            f.write("                <speed>" + str(gpx_track_sample["speed"]) + "</speed>\n")
            f.write("                <extensions>\n")
            f.write("                    <gpxtpx:TrackPointExtension>\n")
            if i < len(hrlist):
                f.write("                        <gpxtpx:hr>" + str(int(hrlist[i][1])) + "</gpxtpx:hr>\n")
            else:
                f.write("                        <gpxtpx:hr>" + "0" + "</gpxtpx:hr>\n")
            f.write("                        <gpxtpx:cad>" + str(float(50+randint(0,60))) + "</gpxtpx:cad>\n")
            f.write("                    </gpxtpx:TrackPointExtension>\n")
            f.write("                </extensions>\n")
            f.write("            </trkpt>\n")
            if previous_gpx_track_sample != "":
                if abs(float(gpx_track_sample["ele"]) - float(previous_gpx_track_sample["ele"])) > max_difference_between_neighbouring_elevation_samples:
                    max_difference_between_neighbouring_elevation_samples = abs(float(gpx_track_sample["ele"]) - float(previous_gpx_track_sample["ele"]))
                    time_of_max_elevation_diff = gpx_track_sample["time"]
                if abs(float(gpx_track_sample["lat"]) - float(previous_gpx_track_sample["lat"])) > max_difference_between_neighbouring_lat_samples:
                    max_difference_between_neighbouring_lat_samples = abs(float(gpx_track_sample["lat"]) - float(previous_gpx_track_sample["lat"]))
                    time_of_max_lat_diff = gpx_track_sample["time"]
                if abs(float(gpx_track_sample["lon"]) - float(previous_gpx_track_sample["lon"])) > max_difference_between_neighbouring_lon_samples:
                    max_difference_between_neighbouring_lon_samples = abs(float(gpx_track_sample["lon"]) - float(previous_gpx_track_sample["lon"]))
                    time_of_max_lon_diff = gpx_track_sample["time"]
                if (gpx_track_sample["time"] - previous_gpx_track_sample["time"]).total_seconds() > max_difference_between_neighbouring_timestamps:
                    max_difference_between_neighbouring_timestamps = (gpx_track_sample["time"] - previous_gpx_track_sample["time"]).total_seconds()
                    time_of_max_time_diff = gpx_track_sample["time"]
                if (gpx_track_sample["time"] - previous_gpx_track_sample["time"]).total_seconds() < min_difference_between_neighbouring_timestamps:
                    min_difference_between_neighbouring_timestamps = (gpx_track_sample["time"] - previous_gpx_track_sample["time"]).total_seconds()
                    time_of_min_time_diff = gpx_track_sample["time"]
            previous_gpx_track_sample = gpx_track_sample
        i = i+1

    f.write(DECATHLONCOACH_GPX_END)

    print("max_difference_between_neighbouring_elevation_samples: ", max_difference_between_neighbouring_elevation_samples)
    print("time_of_max_elevation_diff: ", time_of_max_elevation_diff)
    print("max_difference_between_neighbouring_lat_samples: ", max_difference_between_neighbouring_lat_samples)
    print("time_of_max_lat_diff: ", time_of_max_lat_diff)
    print("max_difference_between_neighbouring_lon_samples: ", max_difference_between_neighbouring_lon_samples)
    print("time_of_max_lon_diff: ", time_of_max_lon_diff)
    print("max_difference_between_neighbouring_timestamps: ", max_difference_between_neighbouring_timestamps)
    print("time_of_max_time_diff: ", time_of_max_time_diff)
    print("min_difference_between_neighbouring_timestamps: ", min_difference_between_neighbouring_timestamps)
    print("time_of_min_time_diff: ", time_of_min_time_diff)
