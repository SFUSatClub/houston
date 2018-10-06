# SFUSat Houston

Named after the coloquial term for the Apollo missions' control centre, Houston is SFUSat's control centre. 

It is a serial monitor, command schedule creator, command uploader, and telemetry verifier. 

![screenshot](docs/screenshot.png?raw=true "Screenshot of early version")

## Installation Mac/Linux
1. run `sudo pip3 install virtualenvwrapper`
2. run `nano ~/.bashrc`
3. At the bottom of your .bashrc file, paste the following lines with ctrl + shift + v

`export WORKON_HOME=$HOME/.virtualenvs`

`export PROJECT_HOME=$HOME/Devel`

`source /usr/local/bin/virtualenvwrapper.sh`

4. exit nano with `ctrl + x`, `y` to save the file
5. cd houston
6. run `which python` and make sure it returns `/usr/local/bin/python`
- If not, run `brew install python` or equivalent install. (Ensure install of Python version 3 `python -V`)
7. ``mkvirtualenv --python=`which python3` sfusat-gcs`` (you can name it whatever you want)
8. You should now be in the virtualenv, indicated by `(sfusat-gcs)` before your command prompt
9. `sudo pip install https://github.com/kivy/kivy/archive/master.zip`
10. `sudo pip install serial`
11. `pip3 install -r requirements.txt`

## Installation in Windows 10
### Initial Setup (skip if pip and Python are already in your path)
1. Open the Command Prompt. Make sure that pip is installed (pip should automatically install with newer versions of python)

>> To check if pip is installed:
   
>> `pip --version`
   
>> This should give you a version and path, if it is installed. If it's not installed, follow the instructions at:
https://projects.raspberrypi.org/en/projects/using-pip-on-windows/4

### Installing Houston
1. run `pip install virtualenvwrapper`
2. In your home directory, find .bash_profile (could also be .bashrc or .profile). Open it and paste the following lines:

  >> `export WORKON_HOME=$HOME/.virtualenvs`
  
  >> `export PROJECT_HOME=$HOME/Devel`

  >> `source [insert path to virtualenvwrapper.sh]` 
  
>> E.g. `source /C/Users/USERNAME/AppData/Local/Programs/Python/Python37-32/Scripts/virtualenvwrapper.sh`

>> Note: It should be possible to use $HOME/AppData/… to describe the path. However, Windows was, when this procedure was first made, unable to handle the whitespace in  username by itself. It was also incapable of finding virtualenvwrapper.sh through    `which virtualenvwrapper.sh` even when virtualenvwrapper.sh was in the path.

3. cd into Houston

4. Create virtual environment:
  >> `mkvirtualenv --python=`which python` orcasat-gcs (the name can be different)`

 >> If this fails: substitute `which python` for the full path of your Python.exe

5. Enter the virtual environment:
  >> `workon orcasat-gcs`

6. Install kivy:
 >> `pip install cython`
 >> `pip install https://github.com/kivy/kivy/archive/master.zip`

>> If this fails, go to the link, download the zip to your computer, and try:

 >> `pip install [pathToDirectoryWithTheZip]/kivy-master.zip`
  
7. Further installs (if install in 6 fails, install these and try again):

  >>`pip install -r requirements.txt`
  
  >> If this fails:
  
  >>`pip install serial`
  
  >>`pip install pygame`
  
  >> `pip install kivy.deps.sdl2`
  
  >> `pip install kivy.deps.glew`
  
  >> `pip install kivy.deps.gstreamer`
  
  >> `pip install kivy.deps.angle`
  
  >> `pip install serial`
  
 8. Try opening the Houston app as indicated under user. If this fails, see if you have all the installs below with `pip list` (shows all your pip installs), and `pip install [whatever is missing]` 
 
 ### Potentially needed pip installs:
 Most of these should automatically come with the steps above:
 - certifi
 - chardet
 - Cython
 - docutils
 - future
 - idna
 - usi8601
 - kivy
 - Kivy-Garden
 - kivy.deps.glew
 - kivy.deps.gstreamer
 - kivy.deps.sdl2
 - pip
 - pygame
 - Pygments
 - pypiwin32
 - pywin32
 - PyYAML
 - requests
 - serial
 - setuptools
 - urllib3
 - wheel


## Installation Notes:

- These steps haven't been thouroughly tested. You might need to jump through some hoops to install Kivy on your system.

## Usage:
1. cd into the repo
2. `workon sfusat-gcs` to enter the virtualenv
3. `python houston.py` to start the app. Serial will automatically connect if the device path is right (see next section).

## Usage notes:

- You will likely need to change the path to the OBC's FTDI usbserial convertor. This is `serialPort` at the top of houston.py. This should be COMx for Windows, /dev/usbserialx for Mac/Linux.
