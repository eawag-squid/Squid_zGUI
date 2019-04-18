# Squid_zGUI
The SQUID_zGUI is (currently) a windows tool designed to ease the fileaccess. This repo contains the Python project (src folder) aswell as the generated installers (deployment)


## SQUID_zGUI PyQt development
The development of the GUI is based on python using PyQT for the graphical representation. A basic tutorial can be found [here](https://build-system.fman.io/pyqt5-tutorial)

### Getting started
We recommend using the Pycharm IDE to develop the Python/PyQT code (download the free community version [here](https://www.jetbrains.com/pycharm/download/#section=windows)). Pycharm (IntelliJ IDE to write python code) does not contain a python interpreter. So we also need to install python ([download link](https://www.python.org/downloads/)) separately on our computer and add the interpreter to our pycharm project (see [this guide](https://www.jetbrains.com/help/pycharm/configuring-local-python-interpreters.html)). 

As interpreter for the initial build we used Python 3.7 and installed the PyQt5 (v5.9.2) and pyserial (v3.4) packages.

For GUI Layout we used the Qt Designer [here](https://build-system.fman.io/qt-designer-download). This application let's you create a .ui file wich then can be loaded in the PyQt project.

### Project structure
The Python code project consist of two classes and the modem package: 
- top class handling the GUI/PyQt objects and instatiating the Zmodem communication class (ZModemAPI).
- ZModemAPI abstracts the zmodem receive and send functions and manages the SQUID menu and Zmodem menu navigation.

<!--- [This link]() leads to the development project. -->

The SQUID_zGUI is a windows tool designed to ease the fileaccess. Underlaying For users preferring to use the commandline, using TeraTerm or implementing their own Zmodem filemanager we provided a submenu with the available file transfer functions contained in the SQUID firmware.

INSERT PICTURE of FILEMANAGER MENU 

### Zmodem Protocol
http://www.ifremer.fr/lpo/gliders/donnees_tt/tech/protocoles/serial_com.pdf

The modem package is based on [this]() github repository with an added send function. 


### SQUID_zGUI deployment and installer creation
#### Prerequisites
- Install fbs using PIP: see this tutorial to get fbs up and running

- In order to create a .exe  file from your Python project the following two SDK's need to be installed and the necessary binary file locations added to the PATH variable:
  - install [Microsoft Visual C++ 2010 Redistributable Package](https://www.microsoft.com/de-ch/download/details.aspx?id=14632)
  - install [Windows 10 SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)
  - add the following directory to the PATH environment variable: "C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit"

- to create a standalone installer fbs uses an application called NSIS:
  - install [NSIS](https://nsis.sourceforge.io/Download)
  - add the following directory to PATH: "C:\Program Files (x86)\NSIS"

 
#### Step by step instructions
1) create fbs project folders via cmd (navigate to or create a dedicated deploy folder in the cmd and run "fbs startproject" - follow the instructions in the cmd.)

2) Copy the whole pycharm project to the newly created fbs directories ..\src\main\python\

3) replace the main.py file with the Squid_zGUI.py file (rename the Squid_zGUI.py -> main.py)
  
4) Python code changes (in main.py):  
   -	add imports for fbs_runtime application context: 
     ```python
     from fbs_runtime.application_context import ApplicationContext
     ```
   - let our Squid_BT_Interface class inherit from the imported ApplicationContext:   
   replace `class Squid_BT_Interface(QtWidgets.QMainWindow):`  
   with `class Squid_BT_Interface(QtWidgets.QMainWindow, ApplicationContext):`
   -	Use the get_resource function to load our pyQT ui file:  
   replace `uic.loadUi("Squid_zGUI.ui", self)`  with `uic.loadUi(self.get_resource('Squid_zGUI.ui'), self)`

5) make folder resources/base/ under ../src/main/[resources/base/] and move the .ui file in the newly created resources folder!

6) add the [SQUID icon](https://github.com/eawag-squid/Squid_zGUI/blob/master/files/icon.ico) to the \src\main\icons\ folder 

7) check if your fbs project is set up correctly by running the cmd command: "fbs run"

8) "compile" the python project to create an executable with "fbs freeze" (this creates the folder ..\target\<project name> containing all dll, binaries and the .exe file that can be zipped and deployed as a standalone windows application)

9) create an NSIS installer with the command: "fbs installer"



<!--- 
pbs freeze

Traceback (most recent call last):
  File "C:\Users\foerstch\AppData\Local\Programs\Python\Python37\Scripts\fbs-script.py", line 11, in <module>
    load_entry_point('fbs==0.7.4', 'console_scripts', 'fbs')()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\__main__.py", line 17, in _main
    fbs.cmdline.main()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\cmdline.py", line 32, in main
    fn(*args)
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\builtin_commands\__init__.py", line 117, in freeze
    freeze_windows(debug=debug)
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\freeze\windows.py", line 22, in freeze_windows
    _add_missing_dlls()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\freeze\windows.py", line 53, in _add_missing_dlls
    ) from None
FileNotFoundError: Could not find msvcr100.dll on your PATH. Please install the Visual C++ Redistributable for Visual Studio 2012 from:
    https://www.microsoft.com/en-us/download/details.aspx?id=30679
    
    
INSTALLED:
Microsoft Visual C++ 2010 Redistributable Package

https://www.microsoft.com/de-ch/download/details.aspx?id=14632


pbs freeze

Traceback (most recent call last):
  File "C:\Users\foerstch\AppData\Local\Programs\Python\Python37\Scripts\fbs-script.py", line 11, in <module>
    load_entry_point('fbs==0.7.4', 'console_scripts', 'fbs')()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\__main__.py", line 17, in _main
    fbs.cmdline.main()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\cmdline.py", line 32, in main
    fn(*args)
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\builtin_commands\__init__.py", line 117, in freeze
    freeze_windows(debug=debug)
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\freeze\windows.py", line 22, in freeze_windows
    _add_missing_dlls()
  File "c:\users\foerstch\appdata\local\programs\python\python37\lib\site-packages\fbs\freeze\windows.py", line 71, in _add_missing_dlls
    ) from None
FileNotFoundError: Could not find api-ms-win-crt-multibyte-l1-1-0.dll on your PATH. If you are on Windows 10, you may have to install the Windows 10 SDK from https://dev.windows.com/en-us/downloads/windows-10-sdk. Otherwise, try installing KB2999226 from https://support.microsoft.com/en-us/kb/2999226. In both cases, add the directory containing api-ms-win-crt-multibyte-l1-1-0.dll to your PATH environment variable afterwards. If there are 32 and 64 bit versions of the DLL, use the 64 bit one (because that's thebitness of your current Python interpreter).

INSTALLED:
https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk

added path:
C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit



AFTER NSIS INSTALL ADD PATH:
C:\Program Files (x86)\NSIS
-->
