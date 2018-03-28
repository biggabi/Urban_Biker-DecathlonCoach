#!/usr/bin/python
from __future__ import print_function

from os import listdir
from os import remove as DELETE_FILE
from os.path import isfile, join, basename, normpath
from datetime import datetime
import re
import sys
import xml.etree.ElementTree as ET

sys.path.append('/home/gabor/gittt/gpxpy-master/gpxpy/')
import gpxpy.parser as parser

from svgpathtools import svg2paths

from DecathlonCoach_format_gpx_fragments import DECATHLONCOACH_GPX_HEADER, DECATHLONCOACH_GPX_END

def find_UB_input_files_in_input_dir(inputdir):
    print('Looking for files in input directory: ', inputdir)
    gpxinputfile = ''
    hrinputfile = ''
    speedinputfile = ''
    altitudeinputfile = ''

    files = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]

    for filename in files:
        gpxinputfile = checkinputfilenames(filename, '.gpx', gpxinputfile, 'GPX')
        hrinputfile = checkinputfilenames(filename, '_duration-heartrate.svg', hrinputfile, 'HR')
        speedinputfile = checkinputfilenames(filename, '_duration-speed.svg', speedinputfile, 'SPEED')
        altitudeinputfile = checkinputfilenames(filename, '_duration-altitude.svg', altitudeinputfile, 'ALTITUDE')

    if gpxinputfile == '':
        print ('ERROR: No GPX file in input directory.')
        sys.exit()
    if hrinputfile == '':
        print ('ERROR: No HR file in input directory.')
        sys.exit()
    if speedinputfile == '':
        print ('ERROR: No speed file in input directory.')
        sys.exit()
    if altitudeinputfile == '':
        print ('ERROR: No altitude file in input directory.')
        sys.exit()

    inputfiles = {'GPX':inputdir+'/'+gpxinputfile, 'HR':inputdir+'/'+hrinputfile, 'speed':inputdir+'/'+speedinputfile, 'altitude':inputdir+'/'+altitudeinputfile}

    return inputfiles

def checkinputfilenames(filename, filenamefragment, inputfile, filetype):
    regextocheck = '[-0-9\.]+' + filenamefragment + '$'
    if re.findall(regextocheck, filename):
        if inputfile == '':
	    inputfile = filename
        else:
	    print ('ERROR: Multiple', filetype, 'files in input directory.')
            sys.exit()
    return inputfile


def parse_GPX_data(gpx_file_name):
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


def parse_HR_data(input_hr_file):
    clean_hr_file = input_hr_file + ".tmp"
    create_clean_svg_file(input_hr_file, clean_hr_file)

    paths, attributes = svg2paths(clean_hr_file, False, True, False, False)

    # Delete clean_hr_file
    DELETE_FILE(clean_hr_file)    

    hr_measurement = []

    for hr_measurement_sample in attributes[0]['points'].split():
        hr_measurement.append([float((hr_measurement_sample.split(',')[0])), float(hr_measurement_sample.split(',')[1])])

    return hr_measurement


def create_clean_svg_file(input_hr_file_name, output_hr_file_name):
    # Remove all polyline data section from svg file that is not 'class="data"' or empty.
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


def create_DecathlonCoach_gpx_file(gpx_track_list, HR_list, inputdir, outputdir):
    f = open(outputdir + "/" + basename(normpath(inputdir)) + "_DecathlonCoach_format.gpx", "w")
    f.write(DECATHLONCOACH_GPX_HEADER)

    max_difference_between_neighbouring_lat_samples = 0
    time_of_max_lat_diff = ""
    max_difference_between_neighbouring_lon_samples = 0
    time_of_max_lon_diff = ""
    max_difference_between_neighbouring_timestamps = 0
    time_of_max_time_diff = ""
    min_difference_between_neighbouring_timestamps = 20
    time_of_min_time_diff = ""
    previous_gpx_track_sample = ""

    i = 0
    for gpx_track_sample in gpx_track_list:
        f.write("            <trkpt lat=\"" + str("%.5f" % gpx_track_sample["lat"]) + "\" lon=\"" + str("%.5f" % gpx_track_sample["lon"]) + "\">\n")
        f.write("                <ele>"+ str(int(gpx_track_sample["ele"])) +"</ele>\n")
        f.write("                <time>" + str(gpx_track_sample["time"])[0:10] + "T" + str(gpx_track_sample["time"])[11:19] + "Z</time>\n")
        f.write("                <speed>" + str(gpx_track_sample["speed"]) + "</speed>\n")
        f.write("                <extensions>\n")
        f.write("                    <gpxtpx:TrackPointExtension>\n")
        if previous_gpx_track_sample != "":
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
        if i < len(HR_list):
            f.write("                        <gpxtpx:hr>" + str(int(HR_list[i][1])) + "</gpxtpx:hr>\n")
	else:
            f.write("                        <gpxtpx:hr>" + "0" + "</gpxtpx:hr>\n")
        f.write("                    </gpxtpx:TrackPointExtension>\n")
        f.write("                </extensions>\n")
        f.write("            </trkpt>\n")
        previous_gpx_track_sample = gpx_track_sample
        i = i+1

    f.write(DECATHLONCOACH_GPX_END)

    print("max_difference_between_neighbouring_lat_samples: ", max_difference_between_neighbouring_lat_samples)
    print("time_of_max_lat_diff: ", time_of_max_lat_diff)
    print("max_difference_between_neighbouring_lon_samples: ", max_difference_between_neighbouring_lon_samples)
    print("time_of_max_lon_diff: ", time_of_max_lon_diff)
    print("max_difference_between_neighbouring_timestamps: ", max_difference_between_neighbouring_timestamps)
    print("time_of_max_time_diff: ", time_of_max_time_diff)
    print("min_difference_between_neighbouring_timestamps: ", min_difference_between_neighbouring_timestamps)
    print("time_of_min_time_diff: ", time_of_min_time_diff)

def str_to_datetime(time_string):
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
