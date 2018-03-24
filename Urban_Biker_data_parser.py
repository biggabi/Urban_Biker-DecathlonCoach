#!/usr/bin/python
from __future__ import print_function

from os import listdir
from os.path import isfile, join
import re
import sys
import xml.etree.ElementTree as ET

sys.path.append('/home/gabor/gittt/gpxpy-master/gpxpy/')
import gpxpy.parser as parser

from svgpathtools import svg2paths


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
        print ('ERROR: No HR file in input directory.')
        sys.exit()
    if altitudeinputfile == '':
        print ('ERROR: No HR file in input directory.')
        sys.exit()

    inputfiles = {'GPX':inputdir+'/'+gpxinputfile, 'HR':inputdir+'/'+hrinputfile, 'speed':inputdir+'/'+speedinputfile, 'altitude':inputdir+'/'+altitudeinputfile}

    return inputfiles

def checkinputfilenames(filename, filenamefregment, inputfile, filetype):
    regextocheck = '[-0-9\.]+' + filenamefregment + '$'
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
                #print('Point at (',point.latitude,'-',point.longitude,'->', point.elevation, '), time (', point.time,'), speed extension:', speed)

    return track_list


def parse_HR_data(hr_file_name):
    print('hr_file_name: ', hr_file_name)
    # Remove all polyline data from svg file that is not 'class="data"'
	#-> ez minidom, de a minidomban nem lehet torolni
		#>>> f = codecs.open('workfile', mode='w', encoding='utf-8')
		#>>> doc = parse("/home/gabor/Dokumentumok/bicajos/20180313/2018-03-13_15-28_duration-heartrate(masolat).svg")
		#>>> doc.writexml(f)
		#>>> f.close()
	#-> https://docs.python.org/3/library/xml.etree.elementtree.html alapjan
		#import xml.etree.ElementTree
		#tree = xml.etree.ElementTree.parse("/home/gabor/Dokumentumok/bicajos/20180313/2018-03-13_15-28_duration-heartrate(masolat).svg")
		#root = tree.getroot()
		#for child in root: print(child.tag, child.attrib)


    paths, attributes = svg2paths(hr_file_name, False, True, False, False)
#    print('Path:', paths)
#    for i in range(0, 10): print('attributes[0][\'points\']', attributes[0]['points'][i])
    print(float(attributes[0]['points'].split()[0].split(',')[0]),
          float(attributes[0]['points'].split()[0].split(',')[1]),
          float(attributes[0]['points'].split()[1].split(',')[0]),
          float(attributes[0]['points'].split()[1].split(',')[1]))
