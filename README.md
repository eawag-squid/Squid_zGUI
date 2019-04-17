# Squid_zGUI
The SQUID_zGUI is a windows tool designed to ease the fileaccess. This repo contains the Python project (src folder) aswell as the generated installers (deployment)


## SQUID_zGUI PyQt development
The development of the GUI is based on python using PyQT for the graphical representation. A basic tutorial can be found [here](https://build-system.fman.io/pyqt5-tutorial)

### Getting started
We recommend using the Pycharm IDE to develop the Python/PyQT code (download the free community version [here](https://www.jetbrains.com/pycharm/download/#section=windows)). Pycharm (IntelliJ IDE to write python code) does not contain a python interpreter. So we also need to install python ([download link](https://www.python.org/downloads/)) separately on our computer and add the interpreter to our pycharm project (see [this guide](https://www.jetbrains.com/help/pycharm/configuring-local-python-interpreters.html)). 

The image below shows the python version and the installed plugins (with the respective version numbers used for the initial build).


For GUI Layout we used the Qt Designer [here](https://build-system.fman.io/qt-designer-download). This application let's you create a .ui file wich then can be loaded in the PyQt project.

### Project structure
The Python code project consist of two classes and the modem package: 
- top class handling the GUI/PyQt objects and instatiating the Zmodem communication class (ZModemAPI).
- ZModemAPI abstracts the zmodem receive and send functions and manages the SQUID menu and Zmodem menu navigation.

<!--- [This link]() leads to the development project. -->

The SQUID_zGUI is a windows tool designed to ease the fileaccess. Underlaying For users preferring to use the commandline, using TeraTerm or implementing their own Zmodem filemanager we provided a submenu with the available file transfer functions contained in the SQUID firmware.

INSERT PICTURE of FILEMANAGER MENU 

### Zmodem Protocol


### SQUID_zGUI windows deployment and installer creation
#### Prerequisites
Install fbs using PIP: see this tutorial to get fbs up and running

#### Step by step instructions
1) create fbs project folders via cmd (navigate to or create a dedicated deploy folder in the cmd and run "fbs startproject" - follow the instructions in the cmd.)

2) Copy the whole pycharm project to the newly created fbs directories (under ..\src\main\python\

3) replace the main.py file with the Squid_zGUI.py file (rename the Squid_zGUI.py -> main.py
  
4) Python code changes (in main.py):  
   -	add imports for fbs_runtime application context… 	
   -	Use get_resource to load our pyQT ui file! -> uic.loadUi(self.get_resource('Squid_zGUI.ui'), self)

5) make folder resources/base/ under ../src/main/[resources/base/] and move the .ui file in the newly created resources folder!

6) check if your fbs project is set up correctly by running the cmd command: "fbs run"

7) "compile" the python project to create an executable with "fbs freeze" (this creates a folder containing all dll, binaries and the exe file that can be zipped and deployed as a standalone windows application)

8) create an NSIS installer with the command: "fbs installer"

> Note: fbs might require additional build/deployment tools as for example: [NSIS installer](https://nsis.sourceforge.io/Download)
