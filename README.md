## Viam Vision Service

This repo gives an example of creating a video stream, using the Viam vision service, and also importing openCV.

The example uses the user's webcam as a robot, adds an object detection model using Viam's vision service, and then draws a box around the object.

This example uses a tflite model with an EfficientDet (created by Google) architecture. It is trained on the COCO 2017 dataset, so it can recognize all sorts of objects including "person", "bus", "toothbrush", etc.  This model, and other applicable tflite models, can be found in the [tensorflow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md).

### Go 
program located in the `go` directory. 
run using `go run cmd.go`

Be sure to change the path to the tflite model in robot_config.json and cmd.go to the full path on your computer.

### Python
program located in the `python` directory.
Needs the [Viam Python SDK](https://github.com/viamrobotics/viam-python-sdk), can download it with `pip install viam-sdk`
run using `python cmd.py`

Be sure to change the path to the tflite model in cmd.py to the full path on your computer.

### app.viam.com

You can also configure a stream of detections completely through the app. You can see an example config in `viam_app_config.json`.
Once you have a robot with a webcam connected to app.viam.com:

In CONFIG -> Services, configure your mlmodel and vision service 
```
{
  "name": "EffDet",
  "type": "mlmodel",
  "model": "tflite_cpu",
  "attributes": {
    "model_path": "/full/path/to/vision-service-examples/data/effdet0.tflite",
    "label_path": "/full/path/to/vision-service-examples/data/effdetlabels.txt",
    "num_threads": 1
  }
},
{
  "name": "myDetector",
  "type": "vision",
  "model": "mlmodel",
  "attributes": {
    "mlmodel_name": "EffDet"
  }
}
```
Then, in CONFIG -> Components, configure both a "webcam" model camera, and a "transform" model camera. 
Give the "transform" model the following attributes:
```
{
  "source": "the_webcam_name",
  "pipeline": [
      {
          "attributes": {
              "confidence_threshold": 0.5,
              "detector_name": "find_objects"
          },
          "type": "detections"
      }
  ]
}
```

Save your config, wait for the robot to reload, and then go to the CONTROL tab to see the stream of detections.

### Note

- The tflite files need to be on the robot, and the path needs to be the path to their location on the robot.  
- Make sure to use full paths to the model and label file when registering the detector.
- If connecting through GRPC, use your robot's address and secret from app.viam.com
- Make sure that the camera name matches in the script and the name of the camera you are using.


