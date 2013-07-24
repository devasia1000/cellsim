This is an automated version of Cellsim that plays a YouTube video, generates real time graphs of stalls
and video resolutions and prints log files to ~/Desktop/log. Cellsim requires the 
following command line arguments:

sudo python start_cellsim_with_internet.py {username} {uplinkTrace} {downlinkTrace} {lossRate} {youtubeVideoLink}

Cellsim also requires that Chromium (available from Devasia's github repo) be setup correctly and that all 
directory paths are configured properly. Cellsim should be stored in ~/cellsim/ and Chromium should be stored in 
~/Desktop/src/. Chromium should be built with system codecs before running Cellsim.

If you run into any trouble compiling/running the code, please don't hesitate to contact me at devasia@mit.edu
