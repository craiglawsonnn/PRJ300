#! /usr/bin/python3
#amazon library
import boto3

#basic libraries from opencv and device information
import io
from PIL import Image
import cv2
from datetime import datetime
import os
import time

#libraries to collect MAC and IP address
import socket
import re,uuid

#libraries for LCD output
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

#library to control gpio for button and LED
import RPi.GPIO as GPIO

#library to get password
import getpass

#initalizing button and LED
GPIO.setmode (GPIO.BOARD)
GPIO.setwarnings(False)

redLED = 18
relay = 13
GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(relay, GPIO.OUT)


def get_wlan_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

devIP = get_wlan_ip_address()
devMAC = (':'.join(re.findall('..', '%012x' % uuid.getnode())))

#initialise LCD screen
lcd=LCD()
def safe_exit(signum, frame):
    exit(1) 
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

# lcd.text("Welcome,", 1)
# lcd.text("Please press button to open", 2)

#initializing what AWS resource to use
s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

#Room number
roomNo = 'B1034'
Pass = True
personName = ""
StudentNumber = 0

#creating the function to send image and metadata to the s3
def sendtos3(Image, Date, Time, Name, studentNo, result, Pass, roomNo, devIP, devMAC):
    file = open(Image,'rb')
    object = s3.Object('logging-data-bucket-prj300', Image)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':str(result), 'Pass':str(Pass), 'RoomNo':roomNo, 'IPAdd':str(devIP), 'MAC':str(devMAC)})

#camport variable can be changed depending on which camera to be used eg 0-1
cam_port = 0

#putting max failure counter as variable if it needs to be changed
maxFailure = 3
counter = 0 #debug
failCounter = 2 #how many fails while the code has been running 
while True:
    # Main loop to run the code continuously
    while failCounter < maxFailure and counter != 0:
        failureWarning = "Attempts left: {}".format(str(maxFailure - failCounter))
        # print(counter)
        GPIO.output(redLED, GPIO.LOW)
        lcd.text("Welcome!", 1, 'center')
        lcd.text("Press button to take a photo", 2, 'center')
        if failCounter != 0:
            lcd.text(str(failureWarning), 4)
        
        # Wait for button press
        inputState = GPIO.input(32)
        

        if inputState == 0:
            print("BUTTON PRESSED")
            inputState = GPIO.input(32)
            cam = cv2.VideoCapture(cam_port)
            
            #image is named exact time and date button is pressed
            image_name = datetime.now().strftime('%Y_%m_%d_%H_%M_%S') +".jpg" #name is exact time and date
            entry_date = datetime.now().strftime('%d/%m/%Y') 
            entry_time = datetime.now().strftime('%H:%M:%S')

            #Informing the user the camera is about to take a photo
            lcd.clear()
            lcd.text("Face the camera in..",1)
            lcd.text("3",2,'center')
            time.sleep(1)
            lcd.text("2",2,'center')
            time.sleep(1)
            lcd.text("1",2,'center')
            time.sleep(1)

            #taking the photo
            image = cam.read()
            # result = image
            cam.release()
            print("Picture taken")

            #lighting the LED
            GPIO.output(redLED, GPIO.HIGH)
            print("LIGHT ON")
            time.sleep(1)
            #turning off the LED
            GPIO.output(redLED, GPIO.LOW)
            
            # saves image
            cv2.imwrite(image_name, image[1])
            
            image = image[1]

            #for debugging
            # shows the image with the image name as the window name
            # cv2.imshow(image_name, image)
            # on a keyboard press, close the window an turn off the camera
            # cv2.waitKey(0)
            # cv2.destroyWindow(image_name)
            
            #converting the image to jpg format and binary to send to S3
            image = Image.open(image_name)
            stream = io.BytesIO()
            image.save(stream,format="JPEG")
            image_binary = stream.getvalue() 

            #try catch block to look for faces
            try:
                # searches the collection for the face
                print("Searching collection")
                response = rekognition.search_faces_by_image(
                    CollectionId='Prj300Rekognition',
                    Image={'Bytes':image_binary}                                       
                    )
                for match in response['FaceMatches']:
                    matchconfidence = round(match['Face']['Confidence'], 4 )
                    
                    #uses the RekognitionId to find the face in dynamo
                    face = dynamodb.get_item(
                        TableName='Prj300',  
                        Key={'RekognitionId': {'S': match['Face']['FaceId']}}
                        )
                    
                if len(response['FaceMatches']) > 0:
                    authorizedMsg = "AUTHORIZED with certainty of {}".format(matchconfidence)

                    personName = face['Item']['FullName']['S']
                    StudentNumber = face['Item']['StudentNo']['S']

                    time.sleep(3)
                    lcd.clear()
                    lcd.text(str(authorizedMsg),1)
                    lcd.text("Door open for..",3)
                    GPIO.output(relay,GPIO.HIGH)
                    print("ONN")
                    lcd.text("5",4,'center')
                    time.sleep(1)
                    lcd.text("4",4,'center')
                    time.sleep(1)
                    lcd.text("3",4,'center')
                    time.sleep(1)
                    lcd.text("2",4,'center')
                    time.sleep(1)
                    lcd.text("1",4,'center')
                    time.sleep(1)
                    GPIO.output(relay,GPIO.LOW)
                    print("OFF")
                    
                    sendtos3(image_name, entry_date, entry_time, personName, StudentNumber ,matchconfidence , 1, roomNo, devIP, devMAC)
                    print("Sent Data to S3")
                
                    #deletes the image from the pi
                    try:
                        os.remove(image_name)
                        print("Passed Image deleted")
                    except:
                        print("Could not delete image")
                    lcd.clear()
                    counter = counter + 1
                    failCounter = 0
                else:
                    print("WHO are you")
                    lcd.clear()
                    lcd.text("FACE not recognised",1)
                    lcd.text("Please contact admin if error persists",2)
                    time.sleep(4)

                    sendtos3(image_name, entry_date, entry_time, "Unknown", "Unknown", "0" ,0,
                         roomNo, devIP, devMAC)
                    
                    try:
                        os.remove(image_name)
                        print("No face Image deleted")
                    except:
                        print("Could not delete image")
                    failCounter = failCounter +1
                    counter = counter + 1
            #runs if there are no faces detected in the image
            except:
                lcd.clear()
                lcd.text("Error, No faces detected!", 1)
                lcd.text("Tip: Try turning on the lights", 3)
                time.sleep(3)
                failCounter = failCounter + 1
                #deletes the image from the pi
                try:
                    os.remove(image_name)
                    print("No faces Image deleted")
                except:
                    print("Could not delete failed image")
                counter = counter + 1
                lcd.clear()
    # Check if the entered password matches the actual password
    # Define the password
    password = "secret"
    # Get the password from the user
    # entered_password = getpass.getpass("Enter the password: ")
    
    lcd.text("Admin required", 1)
    
    # if entered_password == password:
    if password == "secret" :
        print("Access granted.")
        lcd.text("Access granted", 1)
        lcd.text(str(devIP),2)
        time.sleep(3)
        counter = counter + 1
        failCounter = 0
        lcd.clear()
    else:
        print("Access denied.")
        lcd.text("Access denied.", 1)
        time.sleep(3)
        lcd.clear()        

    
