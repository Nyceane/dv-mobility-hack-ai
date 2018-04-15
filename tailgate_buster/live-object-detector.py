#!/usr/bin/python3

# ****************************************************************************
# Copyright(c) 2017 Intel Corporation. 
# License: MIT See LICENSE file in root directory.
# ****************************************************************************

# Detect objects on a LIVE camera feed using
# Intel® Movidius™ Neural Compute Stick (NCS)

import os
import cv2
import sys
import numpy
import ntpath
import argparse
import skimage.io
import skimage.transform

import mvnc.mvncapi as mvnc

from utils import deserialize_output
from utils import visualize_output

import serial

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)

# Detection threshold: Minimum confidance to tag as valid detection
CONFIDANCE_THRESHOLD = 0.40 # 60% confidant

# Variable to store commandline arguments
ARGS                 = None

# OpenCV object for video capture
cam 					= None 
fourcc = None
out = None
# ---- Step 1: Open the enumerated device and get a handle to it -------------
record = True
x = 0
framecount = 0

def open_ncs_device():

    # Look for enumerated NCS device(s); quit program if none found.
    devices = mvnc.EnumerateDevices()
    if len( devices ) == 0:
        print( "No devices found" )
        quit()

    # Get a handle to the first enumerated device and open it
    device = mvnc.Device( devices[0] )
    device.OpenDevice()

    return device

# ---- Step 2: Load a graph file onto the NCS device -------------------------

def load_graph( device ):

    # Read the graph file into a buffer
    with open( ARGS.graph, mode='rb' ) as f:
        blob = f.read()

    # Load the graph buffer into the NCS
    graph = device.AllocateGraph( blob )

    return graph

# ---- Step 3: Pre-process the images ----------------------------------------

def pre_process_image():

    # Grab a frame from the camera
    ret, frame = cam.read()

    # Resize image [Image size is defined by choosen network, during training]
    img = cv2.resize( frame, tuple( ARGS.dim ) )

    # Convert RGB to BGR [skimage reads image in RGB, but Caffe uses BGR]
    if( ARGS.colormode == "BGR" ):
        img = img[:, :, ::-1]

    # Mean subtraction & scaling [A common technique used to center the data]
    img = img.astype( numpy.float16 )
    img = ( img - numpy.float16( ARGS.mean ) ) * ARGS.scale

    return img, frame

# ---- Step 4: Read & print inference results from the NCS -------------------

def infer_image( graph, img, frame ):

    # Load the labels file 
    labels =[ line.rstrip('\n') for line in 
                   open( ARGS.labels ) if line != 'classes\n'] 

    # Load the image as a half-precision floating point array
    graph.LoadTensor( img, 'user object' )

    # Get the results from NCS
    output, userobj = graph.GetResult()

    # Get execution time
    inference_time = graph.GetGraphOption( mvnc.GraphOption.TIME_TAKEN )

    # Deserialize the output into a python dictionary
    output_dict = deserialize_output.ssd( 
                      output, 
                      CONFIDANCE_THRESHOLD, 
                      frame.shape )

    # Print the results
#    print( "I found these objects in "
#            + " ( %.2f ms ):" % ( numpy.sum( inference_time ) ) )

    for i in range( 0, output_dict['num_detections'] ):
#        print( "%3.1f%%\t" % output_dict['detection_scores_' + str(i)] 
#               + labels[ int(output_dict['detection_classes_' + str(i)]) ]
#               + ": Top Left: " + str( output_dict['detection_boxes_' + str(i)][0] )
#               + " Bottom Right: " + str( output_dict['detection_boxes_' + str(i)][1] ) )

        # Draw bounding boxes around valid detections 
        (y1, x1) = output_dict.get('detection_boxes_' + str(i))[0]
        (y2, x2) = output_dict.get('detection_boxes_' + str(i))[1]

        display_str = ( 
                labels[output_dict.get('detection_classes_' + str(i))]
                + ": "
                + str( output_dict.get('detection_scores_' + str(i) ) )
                + "%" )

        global record
        global x
        global fourcc
        global out
        global framecount
        global arduino
        if "car" in display_str or "person" in display_str:
                frame = visualize_output.draw_bounding_box( 
                       y1, x1, y2, x2, 
                       frame,
                       thickness=4,
                       color=(255, 255, 0),
                       display_str=display_str )

        data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
        if data and data.decode("utf-8") == "on":
                if record:
                        fourcc = cv2.VideoWriter_fourcc(*'X264')
                        out = cv2.VideoWriter('output' + str(x) + '.mp4',fourcc, 12.0, (640,480))
                        record = False
                out.write(frame)
                print(str(framecount))
                framecount = framecount + 1
        else:
                if not record and framecount > 50:
                        record = True
                        framecount = 0
                        x = x + 1
                        if out is not None:
                                out.release()
                                out = None
                elif not record:
                        out.write(frame)
                        framecount = framecount + 1
                        print(str(framecount))
    #print( '\n' )

    # If a display is available, show the image on which inference was performed
    if 'DISPLAY' in os.environ:

        cv2.imshow( 'NCS live inference', frame )

# ---- Step 5: Unload the graph and close the device -------------------------

def close_ncs_device( device, graph ):
    graph.DeallocateGraph()
    device.CloseDevice()
    cam.release()
    cv2.destroyAllWindows()

# ---- Main function (entry point for this script ) --------------------------

def main():

    device = open_ncs_device()
    graph = load_graph( device )

    while( True ):
        img, frame = pre_process_image()
        infer_image( graph, img, frame )

        # Display the frame for 5ms, and close the window so that the next frame 
        # can be displayed. Close the window if 'q' or 'Q' is pressed.
        if( cv2.waitKey( 1 ) & 0xFF == ord( 'q' ) ):
            break

    close_ncs_device( device, graph )

# ---- Define 'main' function as the entry point for this script -------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                         description="Object detection using SSD on \
                         Intel® Movidius™ Neural Compute Stick." )

    parser.add_argument( '-g', '--graph', type=str,
                         default='../../caffe/SSD_MobileNet/graph',
                         help="Absolute path to the neural network graph file." )

    parser.add_argument( '-v', '--video', type=int,
                         default=1,
                         help="Index of your computer's V4L2 video device. \
                               ex. 0 for /dev/video0" )

    parser.add_argument( '-l', '--labels', type=str,
                         default='../../caffe/SSD_MobileNet/labels.txt',
                         help="Absolute path to labels file." )

    parser.add_argument( '-M', '--mean', type=float,
                         nargs='+',
                         default=[127.5, 127.5, 127.5],
                         help="',' delimited floating point values for image mean." )

    parser.add_argument( '-S', '--scale', type=float,
                         default=0.00789,
                         help="Absolute path to labels file." )

    parser.add_argument( '-D', '--dim', type=int,
                         nargs='+',
                         default=[300, 300],
                         help="Image dimensions. ex. -D 224 224" )

    parser.add_argument( '-c', '--colormode', type=str,
                         default="RGB",
                         help="RGB vs BGR color sequence. TensorFlow = RGB, Caffe = BGR" )

    ARGS = parser.parse_args()

    # Construct (open) the camera
    cam = cv2.VideoCapture( ARGS.video )

    main()

# ==== End of file ===========================================================
