# Urban_Biker-DecathlonCoach

This project is a converter from the output files -gpx and svgs- of Urban Biker app to the format that the DecathlonCoach app can handle as input.

Some packages need to be installed with pip install:
    pip install gpxpy
    pip install svgpathtools

Input parameters
    -i    input directory, where the track data is stored in a .gpx file, additional data, like heartrate, cadence in .svg files
    -o    output directory, where the output file(s) that can be loaded into DecathlonCoach are saved
    -s    s for split, as DecathlonCoach can input only limited lenght of tracks, so in this mode the orginal track is split to sub-tracks that have a maximum lenght of 2950 samples; could be used together with -d, though this functionality is not implemented yet
    -d    d is for decreased granularity in order to have an output file, which is not longer than 2950 samples; can be used together with -s

Limitations:
    Though cadance data can be saved in the output file of the program -though at the moment only in a simulated way, as I do not have yet real measured data- and DecathlonCoach does not hang on such file as input, this data is still not shown in DecathlonCoach training sessions. "Geonaute Request # 98977" is opened to clarify it.
