from watson_developer_cloud import VisualRecognitionV3 as visual_recognition
import picamera
import json

#initialize the camera
camera=picamera.PiCamera()
camera.rotation = 180

#capture image
camera.capture('image.jpg')

vr = visual_recognition(
    api_key='3fdf52a6351df0095ba74b2b1371b90086f1785f',
    version='2016-05-20')

with open ('./image.jpg', 'rb') as images_file:
    #analysis = vr.classify(images_file, parameters = json.dumps({'classifier_ids': ["default"]}))
    people = vr.detect_faces(images_file)
    
#response = analysis['images'][0]['classifiers'][0]['classes']

#answer = ""
#score = 0
#for r in range(0, len(response)):
#    if response[r]['score'] > score:
#        answer = response[r]['class']
#        score = response[r]['score']

#print("i'm {:.0%} percent certain that I see a {}".format(score, answer))

#for x in range(0, len(response)):
#    print('{} : {}'.format(response[x]['class'], response[x]['score']))
    
print(json.dumps(people, indent=2))
