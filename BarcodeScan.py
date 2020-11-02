# USAGE
# python barcode_scanner_video.py

# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
from pyzbar import pyzbar
from multiprocessing import Process
import argparse
import datetime
import imutils
import time
import cv2
import csv

# RGB COLOR
import pigpio

pi = pigpio.pi()

RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 24

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# open the output CSV file for writing and initialize the set of
# barcodes found thus far
# csv = open(args["output"], "w")
found = set()

def changecolor():
    pi.set_PWM_dutycycle(RED_PIN, row['r'])
    pi.set_PWM_dutycycle(GREEN_PIN, row['g'])
    pi.set_PWM_dutycycle(BLUE_PIN, row['b'])
    print("Detected: " + row['name'] + ". Changing color to " + row['r'] + ", " + row['g'] + ", " + row[
        'b'])


# loop over the frames from the video stream

while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)

    # loop over the detected barcodes
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw
        # the bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Camera will recognize the QR scanner, grab the RGB values from the
        # datatbase and change the color
        with open('AlbumDatabase3.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if barcodeData == row['name']:
                    changecolor()

        # csv.write("{}\n".format(barcodeData))
        # csv.flush()
        # found.add(barcodeData)

    # If the Camera does not recognize a QR code, it will automatically turn off the RGB strips

    # show the output frame
    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    elif key == ord("p"):
        pi.set_PWM_dutycycle(RED_PIN, 0)
        pi.set_PWM_dutycycle(GREEN_PIN, 0)
        pi.set_PWM_dutycycle(BLUE_PIN, 0)

        print("Resetting lights back to default")


# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up and shutting down RGB")
# csv.close()
pi.set_PWM_dutycycle(RED_PIN, 0)
pi.set_PWM_dutycycle(GREEN_PIN, 0)
pi.set_PWM_dutycycle(BLUE_PIN, 0)
cv2.destroyAllWindows()
vs.stop()
