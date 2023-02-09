#amazon library
import boto3

#basic libraries from opencv and device information
import io
from PIL import Image
import cv2
from datetime import datetime
import os
import time

#libraries for LCD output
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

#library to control gpio for button and LED
import RPi.GPIO as GPIO

#initalizing button and LED
GPIO.setmode (GPIO.BOARD)
GPIO.setwarnings(False)

redLED = 18
GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_UP)
redButtonState = GPIO.input(32)

#initialise LCD screen
lcd=LCD()
def safe_exit(signum, frame):
    exit(1) 
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

lcd.text("Welcome,", 1)
lcd.text("Please press button to open", 2)

     
#initializing what AWS resource to use
s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition', region_name='eu-west-1')
dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

#creating the function to send image and metadata to the s3
def sendtos3(Image, Date, Time, Name, studentNo, result):
    file = open(Image,'rb')
    object = s3.Object('prj300-website', Image)
    ret = object.put(Body=file, Metadata={'Date': Date,'Time': Time,'FullName':Name, 'StudentNo':studentNo, 'Match':result})

#camport variable can be changed depending on which camera to be used eg 0-1
cam_port = 0
image_name = datetime.now().strftime('%d_%m_%Y_%H_%M_%S') #name is exact time and date
entry_date = datetime.now().strftime('%d/%m/%Y')
entry_time = datetime.now().strftime('%H:%M:%S')


cam = cv2.VideoCapture(cam_port)
 

game = True

while game:
    redButtonState = GPIO.input(32)
    if redButtonState == 0:
        GPIO.output(redLED, GPIO.HIGH)
        lcd.clear()
        
if result:
 # shows the image with the image name as the window name
    cv2.imshow(image_name, image)
# saves image
    cv2.imwrite(image_name+".jpg", image)
# on a keyboard press, close the window an dturn off the camera
    cv2.waitKey(0)
    cv2.destroyWindow(image_name)
    cam.release()

# If captured image is corrupted, ouputting error
else:
    print("No image detected.")
    lcd.text("No image detected",1)
    pause()


#open the image
image = Image.open(image_name + ".jpg")
stream = io.BytesIO()
image.save(stream,format="JPEG")
image_binary = stream.getvalue()

# searches the collection for the face
response = rekognition.search_faces_by_image(
        CollectionId='Prj300Rekognition',
        Image={'Bytes':image_binary}                                       
        )

found = False
#for loop if multiple images are seen 
for match in response['FaceMatches']:
    matchconfidence = round(match['Face']['Confidence'], 9 )
    print(matchconfidence)
    lcd.text(str(matchconfidence),1)
    pause()
    
    #uses the RekognitionId to find the face in dynamo
    face = dynamodb.get_item(
        TableName='Prj300',  
        Key={'RekognitionId': {'S': match['Face']['FaceId']}}
        )
    #checks if there is a face, get the metadata e.g name and student no.
    if 'Item' in face:
        personName=face['Item']['FullName']['S']
        StudentNumber= face['Item']['StudentNo']['S']
        print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
        lcd.text = ("YES",1)
        pause()
        found = True
        sendtos3(image_name +'.jpg', entry_date, entry_time, personName, StudentNumber, str(matchconfidence))
        #deletes the image from my own laptop
        os.remove(image_name+".jpg")
    if not found:
        print("Person cannot be recognized")
        lcd.text = ("Unauthorized User", 1)
        pause()
    s3 = boto3.resource('s3')
    GPIO.output(redLED, GPIO.LOW)
   
   
 
# reading the input using the camera
result, image = cam.read()

# 
# if result:
#  # shows the image with the image name as the window name
#     cv2.imshow(image_name, image)
# # saves image
#     cv2.imwrite(image_name+".jpg", image)
# # on a keyboard press, close the window an dturn off the camera
#     cv2.waitKey(0)
#     cv2.destroyWindow(image_name)
#     cam.release()
# 
# # If captured image is corrupted, ouputting error
# else:
#     print("No image detected.")
#     lcd.text("No image detected",1)
#     pause()
# 
# 
# #open the image
# image = Image.open(image_name + ".jpg")
# stream = io.BytesIO()
# image.save(stream,format="JPEG")
# image_binary = stream.getvalue()
# 
# # searches the collection for the face
# response = rekognition.search_faces_by_image(
#         CollectionId='Prj300Rekognition',
#         Image={'Bytes':image_binary}                                       
#         )
# 
# found = False
# #for loop if multiple images are seen 
# for match in response['FaceMatches']:
#     matchconfidence = round(match['Face']['Confidence'], 9 )
#     print(matchconfidence)
#     lcd.text(str(matchconfidence),1)
#     pause()
#     
#     #uses the RekognitionId to find the face in dynamo
#     face = dynamodb.get_item(
#         TableName='Prj300',  
#         Key={'RekognitionId': {'S': match['Face']['FaceId']}}
#         )
#     #checks if there is a face, get the metadata e.g name and student no.
#     if 'Item' in face:
#         personName=face['Item']['FullName']['S']
#         StudentNumber= face['Item']['StudentNo']['S']
#         print ("Found Person: Name:", face['Item']['FullName']['S'], ", Student No:", face['Item']['StudentNo']['S'])
#         lcd.text = ("YES",1)
#         pause()
#         
#         found = True
#         
#         sendtos3(image_name +'.jpg', entry_date, entry_time, personName, StudentNumber, str(matchconfidence))
#         #deletes the image from my own laptop
# os.remove(image_name+".jpg")
# if not found:
#     print("Person cannot be recognized")
#     lcd.text = ("Unauthorized User", 1)
#     pause()
# s3 = boto3.resource('s3')
