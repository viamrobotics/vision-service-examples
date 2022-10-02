
## OpenCV with Viam 

This repo gives an example of creating a video stream, using the Viam vision service, and also importing openCV.

The example uses the user's webcam as a robot, adds an object detection model using Viam's vision service, and then draws a box around the object using OpenCV.

It uses an EfficientDet tflite model from the [tensorflow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md).

### Go 
program located in `opencv/go` 
run using `go run cmd.go`

### Python
program located in `opencv/python`
Needs the Viam Python SDK, can download it with `pip install git+https://github.com/viamrobotics/python-sdk.git`
run using `python cmd.py`


### Note

- The tflite files need to be on the robot, and the path needs to be the path to their location on the robot.  
- Make sure to use full paths to the model and label file when registering the detector.
- If connecting through GRPC, use your robot's address and secret from app.viam.com
- Make sure that the camera name matches in the script and the name of the camera you are using.


