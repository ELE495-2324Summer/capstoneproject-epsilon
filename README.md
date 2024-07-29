[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5mCoF9-h)
# TOBB ETÜ ELE495 - Capstone Project

# Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Acknowledgements](#acknowledgements)

## Introduction
Aim of this project is autonomous parking with JetBot. Jetson Nano 2GB Developer Kit is used as main board. Besides this board, others components of JetBot are motors, IMX219-160 camera, camera holder, caster, power adapter, wireless gamepad, battery charger, wireless gamepad, screw driver, cable, screw pack, 4010 cooling fan, microSD card reader.These components help JetBot to find right plate which is allocated for it.

## Features
- Hardware: Jetson Nano 2GB Developer Kit(https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit)
- Operating System and packages: JetPack SDK(Ubuntu 18.04 LTS or upper)
- Features of main components:
    - motors and casters: for movement
    - IMX219-160: for detection of road and parking plates
    - HC-SR04(ultrasonic distance sensor): for detection of distance(it ensures avoidance of crash)
    - TCS34725(color sensor): for avoidance of park boundaries
    - microSD: in order to write JetPack SDK to Jetson Nano
    - Other components are for JetBot assembly.
    

## Installation
Describe the steps required to install and set up the project. Include any prerequisites, dependencies, and commands needed to get the project running.
1) Install the corresponding image to SD card using Ecther(https://jetbot.org/master/software_setup/sd_card.html)
2) Connect your flashed SD card to your Jetson Board.
3) You need to configure Wi-Fi connection to your Jetson Board. In order to do that create a hotspot using your smart phone, computer etc. Important point is that your hotspot newtork name and password must be fixed because your JetBot will be using that during the project.
4) After completing these steps hotspot must be connected to JetBot. To do that plug your JetBot to your computer and open PuTTy(https://www.putty.org/) terminal. Select Connection type as Serial and write your Serial line port. Write the speed as 115200 b/s and press Open.
5) After completing 4th step you must be able to visiualize command windows. Enter your Wi-Fi name and password to this code : 
   "$ sudo nmcli device wifi connect <MY_WIFI_AP> password <MY_WIFI_PASSWORD>" 
    And press enter to finish your Wi-Fi configuration. Now you must be able to connect your hotspot point automatically. 
    Now you can unplug your cable.
6) Now you can visiulazie your IP address onto JetBot screen.
7) Open up your browser and enter "Your IP address":8888
8) Now you can access JupyterLab. This is the place where we implement our project.
9) As mentioned, Jetbot performs autonomous parking. To start that process you must install app-release.apk to your android device.

## Usage
Installation process has been completed at previous step. Now we will perform autonomus parking. 
1) Create a new folder at main directory.
2) Upload all .ipynb and .py files to folder that you have created.
3) Open the application that is in your android device.
4) Open the file that is named as haberlesme.ipynb and run the first cell.
5) Enter your IP address to application.
6) If you did not place your JetBot to platform, place the JetBot to proper location on platform. JetBot must see the black line vertically from that location.
7) Enter your desired plate to application.
8) Wait until parking process finishes.

## Screenshots
Some images from project:


![Logo](https://github.com/ELE495-2324Summer/capstoneproject-epsilon/blob/main/Images/img_1.jpg)


- Parking process examples:
- https://www.youtube.com/watch?v=28I-RleOdqU
-
- https://www.youtube.com/watch?v=6cVpPMTL9zc



## Acknowledgements
Here are the contributors.

[Contributor 1](https://github.com/Seteney)
[Contributor 2](https://github.com/eren-caglar)
[Contributor 3](https://github.com/cetingulec)
[Contributor 4](https://github.com/RecaiEfeDik)
[Resource](https://www.nvidia.com)
