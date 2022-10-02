
## Viam Vision Service

This repo gives an example of creating a video stream, using the Viam vision service, and also importing openCV.

The example uses the user's webcam as a robot, adds an object detection model using Viam's vision service, and then draws a box around the object.

It uses an EfficientDet tflite model from the [tensorflow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md).

### Go 
program located in `opencv/go` 
run using `go run cmd.go`

### Python
program located in `opencv/python`
Needs the [Viam Python SDK](https://github.com/viamrobotics/viam-python-sdk), can download it with `pip install git+https://github.com/viamrobotics/python-sdk.git`
run using `python cmd.py`

### app.viam.com

You can also configure a stream of detections completely through the app. You can see an example config in `viam_app_config.json`.
Once you have a robot with a webcam connected to app.viam.com:

In CONFIG -> Services, configure your object detection model
```
{
  "register_models": [
    {
      "parameters": {
        "model_path": "/full/path/to/vision-service-examples/data/effdet0.tflite",
        "num_threads": 1
      },
      "name": "find_objects",
      "type": "tflite_detector"
    }
  ]
}
```
Then, in CONFIG -> Components, configure both a "webcam" model camera, and a "transform" model camera. 
Give the "transform" model the following attributes:
```
"stream": "color",
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
```

Save your config, wait for the robot to reload, and then go to the CONTROL tab to see the stream of detections.

### Note

- The tflite files need to be on the robot, and the path needs to be the path to their location on the robot.  
- Make sure to use full paths to the model and label file when registering the detector.
- If connecting through GRPC, use your robot's address and secret from app.viam.com
- Make sure that the camera name matches in the script and the name of the camera you are using.


