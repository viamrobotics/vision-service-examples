package main

import (
	"context"
	"image/color"

	"github.com/edaniels/golog"
	"go.viam.com/rdk/components/camera"
	"go.viam.com/rdk/config"
	robotimpl "go.viam.com/rdk/robot/impl"
	"go.viam.com/rdk/services/vision"
	"gocv.io/x/gocv"

	// registers all cameras.
	_ "go.viam.com/rdk/components/camera/register"
	// registers the vision service
	_ "go.viam.com/rdk/services/vision/register"
)

func main() {
	logger := golog.NewDevelopmentLogger("opencv")
	// read the robot config and create the robot
	// if you want to create the robot directly from a JSON
	r, err := robotimpl.RobotFromConfigPath(context.Background(), "camera_config.json", logger)
	if err != nil {
		logger.Fatalf("cannot create robot: %v", err)
	}
	/* if you want to read the robot from the app
	r, err := client.New(
		context.Background(),
		"[THE ADDRESS OF YOUR ROBOT, GOTTEN FROM THE CONNECT TAB]",
		logger,
		client.WithDialOptions(rpc.WithCredentials(rpc.Credentials{
			Type:    utils.CredentialsTypeRobotLocationSecret,
			Payload: "[THE SECRET OF YOUR ROBOT GOTTEN FROM THE CONNECT TAB]",
		})),
	)
	if err != nil {
		logger.Fatalf("cannot create robot: %v", err)
	}
	*/
	defer r.Close(context.Background())
	logger.Info("Resources:")
	logger.Info(r.ResourceNames())
	// grab the camera from the robot
	cameraName := "cam1" // make sure to use the same name as in the json/APP
	cam, err := camera.FromRobot(r, cameraName)
	if err != nil {
		logger.Fatalf("cannot get camera: %v", err)
	}
	camStream, err := cam.Stream(context.Background())
	if err != nil {
		logger.Fatalf("cannot get camera stream: %v", err)
	}
	// grab Viam's vision service to add a TF-Lite model for person detection
	visionSrv, err := vision.FirstFromRobot(r)
	if err != nil {
		logger.Fatalf("cannot get vision service: %v", err)
	}
	err = visionSrv.AddDetector(
		context.Background(),
		vision.VisModelConfig{
			Name: "find_objects",
			Type: "tflite_detector",
			Parameters: config.AttributeMap{
				"model_path":  "/full/path/to/vision-service-examples/data/effdet0.tflite",
				"label_path":  "/full/path/to/vision-service-examples/data/effdetlabels.txt",
				"num_threads": 1,
			},
		},
	)
	if err != nil {
		logger.Fatalf("cannot add tflite model: %v", err)
	}
	// make the display window and get the camera stream
	window := gocv.NewWindow("Object Detect")
	defer window.Close()
	// loop forever, find the person using Viam Vision, and draw the box using openCV
	for {
		// get image
		img, release, err := camStream.Next(context.Background())
		if err != nil {
			logger.Fatalf("cannot get image: %v", err)
		}
		defer release()
		// get detection bounding boxes
		detections, err := visionSrv.Detections(context.Background(), img, "find_objects")
		if err != nil {
			logger.Errorf("detection error: %v", err)
			continue
		}
		mat, err := gocv.ImageToMatRGBA(img)
		if err != nil {
			logger.Errorf("error converting image to OpenCV Mat type: %v", err)
			continue
		}
		// get the objects that appears above a certain confidence
		labels := make([]string, 0, 25)
		for _, d := range detections {
			if d.Score() > 0.6 {
				boundingBox := d.BoundingBox()
				// draw rectangle around the object
				gocv.Rectangle(&mat, *boundingBox, color.RGBA{255, 0, 0, 255}, 3)
				labels = append(labels, d.Label())
			}
		}
		logger.Infof("found these objects in image: %v", labels)
		// display
		window.IMShow(mat)
		window.WaitKey(1)
	}

}
