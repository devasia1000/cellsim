Instructions for running Chromium over Cellsim:

1) Run 'start_cellsim_with_internet.py'
2) Five XTERM terminals should pop up 
3) In the 'cellsim' XTERM, run 'perl routing_tables.pl'
4) In the 'cellsim' XTERM, run 'perl start_cellsim.pl'
5) In the 'client' XTERM, navigate to Chromium's src directory and run 'start_test.sh'
6) Chromium should open and the video should start playing - log files will be written to ~/Desktop/log/
7) Use gnuplot to plot graphs of log files
