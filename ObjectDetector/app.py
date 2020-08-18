import time
from absl import app, logging
import cv2
import numpy as np
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images, load_tfrecord_dataset
from yolov3_tf2.utils import draw_outputs
from flask import Flask, render_template,request, Response, jsonify, send_from_directory, abort
import os
from werkzeug import secure_filename
app = Flask(__name__)

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

# customize your API through the following parameters
classes_path = './data/labels/coco.names'
weights_path = './weights/yolov3.tf'
tiny = False                    # set to True if using a Yolov3 Tiny model
size = 416                      # size images are resized to for model
output_path = './detections/'   # path to output folder where images with detections are saved
num_classes = 80                # number of classes in model

# load in weights and classes
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

if tiny:
    yolo = YoloV3Tiny(classes=num_classes)
else:
    yolo = YoloV3(classes=num_classes)

yolo.load_weights(weights_path).expect_partial()
print('weights loaded')

class_names = [c.strip() for c in open(classes_path).readlines()]
print('classes loaded')

# Initialize Flask application
app = Flask(__name__)

@app.route('/upload')
def upload_file():
   return render_template('upload.html')

@app.route('/detections', methods=['POST'])
def get_detections():
    raw_images = []
    images = request.files.getlist("images")
    image_names = []
    for image in images:
        image_name = image.filename
        image_names.append(image_name)
        image.save(os.path.join(os.getcwd(), image_name))
        img_raw = tf.image.decode_image(
            open(image_name, 'rb').read(), channels=3)
        raw_images.append(img_raw)
        
    num = 0
    
    # create list for final response
    response = []
    category = []

    for j in range(len(raw_images)):
        # create list of responses for current image
        responses = []
        raw_img = raw_images[j]
        num += 1
        img = tf.expand_dims(raw_img, 0)
        img = transform_images(img, size)

        t1 = time.time()
        boxes, scores, classes, nums = yolo(img)
        t2 = time.time()
        print('time: {}'.format(t2 - t1))

        # print('detections:')
        for i in range(nums[0]):
            print('\t{}, {}, {}'.format(class_names[int(classes[0][i])], np.array(scores[0][i]), np.array(boxes[0][i])))
            responses.append({
                "class": class_names[int(classes[0][i])],
                "confidence": float("{0:.2f}".format(np.array(scores[0][i])*100))
            })
            
        response.append({
            "image": image_names[j],
            "detections": responses
        })
    for a in response:
        detected_classes = []
        detected_confidences = []

        number_of_classes = {'people': 0, 'vehicles': 0, 'aeroplane': 0, 'animalsBirds': 0, 'sports': 0, 'dining': 0, 'food': 0, 'furniture': 0, 'electricAppliances': 0, 'bags': 0, 'householdgoods': 0, 'others': 0}

        confidence_of_classes = {'people': 0, 'vehicles': 0, 'aeroplane': 0, 'animalsBirds': 0, 'sports': 0, 'dining': 0, 'food': 0, 'furniture': 0, 'electricAppliances': 0, 'bags': 0, 'householdgoods': 0, 'others': 0}

        b = a['detections']
        if(b == []):
            confidence_of_classes['others'] += 1
        elif(b != []):
            for c in b:
                detected_classes.append(c['class'])
                detected_confidences.append(c['confidence'])

        for i in range(0,len(detected_classes)):
            if detected_classes[i] == 'person':
                number_of_classes['people'] += 1
                confidence_of_classes['people'] += detected_confidences[i]
            elif detected_classes[i] == 'bicycle' or detected_classes[i] == 'car' or detected_classes[i] == 'motorbike' or detected_classes[i] == 'bus' or detected_classes[i] == 'train' or detected_classes[i] == 'truck' or detected_classes[i] == 'boat' or detected_classes[i] == 'traffic light' or detected_classes[i] == 'stop sign' or detected_classes[i] == 'parking meter':
                number_of_classes['vehicles'] += 1
                confidence_of_classes['vehicles'] += detected_confidences[i]
            elif detected_classes[i] == 'aeroplane':
                number_of_classes['aeroplane'] += 1
                confidence_of_classes['aeroplane'] += detected_confidences[i]
            elif detected_classes[i] == 'bird' or detected_classes[i] == 'cat' or detected_classes[i] == 'dog' or detected_classes[i] == 'horse' or detected_classes[i] == 'sheep' or detected_classes[i] == 'cow' or detected_classes[i] == 'elephant' or detected_classes[i] == 'bear' or detected_classes[i] == 'zebra' or detected_classes[i] == 'giraffe':
                number_of_classes['animalsBirds'] += 1
                confidence_of_classes['animalsBirds'] += detected_confidences[i]
            elif detected_classes[i] == 'frisbee' or detected_classes[i] == 'skis' or detected_classes[i] == 'snowboard' or detected_classes[i] == 'sports ball' or detected_classes[i] == 'kite' or detected_classes[i] == 'baseball bat' or detected_classes[i] == 'baseball glove' or detected_classes[i] == 'skateboard' or detected_classes[i] == 'surfboard' or detected_classes[i] == 'tennis racket':
                number_of_classes['sports'] += 1
                confidence_of_classes['sports'] += detected_confidences[i]
            elif detected_classes[i] == 'bottle' or detected_classes[i] == 'wine glass' or detected_classes[i] == 'cup' or detected_classes[i] == 'fork' or detected_classes[i] == 'knife' or detected_classes[i] == 'spoon' or detected_classes[i] == 'bowl' or detected_classes[i] == 'microwave' or detected_classes[i] == 'oven' or detected_classes[i] == 'toaster' or detected_classes[i] == 'sink' or detected_classes[i] == 'refrigerator':
                number_of_classes['dining'] += 1
                confidence_of_classes['dining'] += detected_confidences[i]
            elif detected_classes[i] == 'banana' or detected_classes[i] == 'apple' or detected_classes[i] == 'sandwich' or detected_classes[i] == 'orange' or detected_classes[i] == 'broccoli' or detected_classes[i] == 'carrot' or detected_classes[i] == 'hot dog' or detected_classes[i] == 'pizza' or detected_classes[i] == 'donut' or detected_classes[i] == 'cake':
                number_of_classes['food'] += 1
                confidence_of_classes['food'] += detected_confidences[i]
            elif detected_classes[i] == 'chair' or detected_classes[i] == 'sofa' or detected_classes[i] == 'bed' or detected_classes[i] == 'diningtable' or detected_classes[i] == 'bench':
                number_of_classes['furniture'] += 1
                confidence_of_classes['furniture'] += detected_confidences[i]
            elif detected_classes[i] == 'tvmonitor' or detected_classes[i] == 'laptop' or detected_classes[i] == 'mouse' or detected_classes[i] == 'remote' or detected_classes[i] == 'keyboard' or detected_classes[i] == 'cell phone':
                number_of_classes['electricAppliances'] += 1
                confidence_of_classes['electricAppliances'] += detected_confidences[i]
            elif detected_classes[i] == 'backpack' or detected_classes[i] == 'handbag' or detected_classes[i] == 'suitcase':
                number_of_classes['bags'] += 1
                confidence_of_classes['bags'] += detected_confidences[i]
            elif detected_classes[i] == 'pottedplant' or detected_classes[i] == 'clock' or detected_classes[i] == 'vase':
                number_of_classes['householdgoods'] += 1
                confidence_of_classes['householdgoods'] += detected_confidences[i]
            elif detected_classes[i] == 'fire hydrant' or detected_classes[i] == 'umbrella' or detected_classes[i] == 'tie' or detected_classes[i] == 'book' or detected_classes[i] == 'scissors' or detected_classes[i] == 'teddy bear' or detected_classes[i] == 'toilet' or detected_classes[i] == 'toothbrush' or detected_classes[i] == 'hair drier':
                number_of_classes['others'] += 1
                confidence_of_classes['others'] += detected_confidences[i]

        maxConfidence = max(confidence_of_classes, key=confidence_of_classes.get)
        category.append(maxConfidence)

    for name in image_names:
        os.remove(name)
    try:
        return str(category[0]), 200
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port=5000)