![logo][Logo_Large.jpg]
# Tailgate Buster
We built Tailgate Buster, to sense tailgating and prevent accidents.

# Team AI
Peter Ma - IoT tailgating detector, AI detection

Brian Cottrell - Web/Mobile App

Xiaobi (Iris) Pan - UI/UX Design, Industrial Design

Our deck can be viewed at 
https://docs.google.com/presentation/d/1OyHM0VFQi8pevPmodofPLgmWqNdF-mQWB6Of6JgRzls/edit?usp=sharing

# Code Structure
There are few pieces of the code here.
1) AI + IoT portion Portion, we used Ubuntu and Movidius NCS.  This requires you to download
https://github.com/movidius/ncsdk
https://github.com/movidius/ncappzoo
Using object detection to use Mobile-SSD-Net to launch inference with the Convolutional Neural Network to determine up to 20 subjects, we are specifically looking for Person and Cars.  This helps us to determine whether we should record the video.

2) Arduino portion
Arduino is rather simple, we place sonic ranger on D6, and backlight LED Display on I2C port of Arduino, the Ubuntu can can interact with it via test_arduino.py

3) License detection portion, pretty straight forward, we modified open sourcing project
https://github.com/MicrocontrollersAndMore/OpenCV_3_License_Plate_Recognition_Python

