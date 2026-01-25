<div align="center">
<img src="https://github.com/user-attachments/assets/56b16f14-efc8-4bec-9d7f-9fd81e67fb2c"
  width="500"
/>

# ShellOS
</div>
ShellOS is a basic OS-Like non-bootable enviroment made in Python for Windows x64 combines elements of Windows and Linux into one, it has it's own Shell and Commands, its own GUI

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Filesystem Layout](#filesystem-layout)
- [ShellOS Packaging Tool](#spt)
- [ShellOS Scripting Language](#ShellOS-Scripting-Language)
- [Known Limitations](#known-limitations)

## Features 
ShellOS is basic for python however comes with a decent amount of features such as

 - A Full Graphical UI
 - A login system
 - A Command Shell
 - It's own Custom Commands
 - It's own Web Browser
 - It's own Scripting Language
 - It's Own Package Manager

## Prerequisites
ShellOS needs a few things before running
[Python 3.13.5 or later](https://www.python.org/downloads/release/python-3135/) (3.8 can work and you can modify startup to bypass however not offically supported)
Windows 7, 8.1, 10 or 11
The following pip packages (normally install automatically upon startup
 - Pygame (GUI)
 - Tkinter (Older & Basic Apps, Usually included with Python on windows)
 - customtkinter (Most Modern ShellOS Apps)
 - Psutil
 - PyQt5 (ShellOS Internet Browser)
 - PyQtWebEngine (ShellOS Internet Browser)
 - tkcalendar
 - py-cpuinfo (CPU Information)
 - keyboard
 - pywin32
 - Pillow (Image Display)
System Requirements:
x86_64 CPU thats 500MHz and 1 Core or better
1GB of Ram (available)
5GB of Storage (available) (includes Python, Pip Packages and ShellOS)

## Setup
There are 2 options of ShellOS you can download that is the portable .zip file and the .exe installer 
To setup via the installer download the .exe from the releases labeled ShellOS-X.X-Win-x64-Setup.exe and run it Windows **__WILL__** mark the exe as unsafe, let it run as its safe just not signed and it will guide you through, preferably install ShellOS on the root of the C: Drive or even a USB/External Drive then run ShellOS from the start menu

To Setup via the Portable Zip download the .zip from the releases labeled ShellOS-X.X.zip and then download extract the zip preferably to the root of a drive or the documents folder then run ShellOS.py

## Filesystem Layout
ShellOS's root Filesystem folder is layed out fairly similar to Windows 
+---Dcoumentation
+---SYSTEM
|   +---Graphical_Shell
|   |   +---backgrounds
|   |   +---icons
|   |   +---sounds
|   |   \---__pycache__
|   \---__pycache__
+---System64
|   +---Cmdlets
|   +---documents
|   |   +---Downloads
|   |   +---Music
|   |   +---Pictures
|   |   \---Videos
|   +---programs
|   |   +---games
|   |   \---ShellOS-Browser
|   +---resources
|   |   +---icons
|   |   \---images
|   +---SettingsApplets
|   \---ShellOS-Scripting-Language
\---sysres
    \---System64
requirements.txt
ShellOS.py

## SPT
SPT is the ShellOS package manager for ShellOS, it is very limited and packages are hosted in the ShellOS-Packages repo install or uninstall packages using SPT Install or SPT Uninstall 

## ShellOS Scripting Language 
Syntax can be found in the SSL Folder in System64

## Known Limitations
- SPT functionality is limited
- ShellOS Scripting Language is very limited
- os runs slower
- ShellOS Internet functionality is limited

</div>

