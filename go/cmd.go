package main

import (
	"context"
	"image"

	"github.com/edaniels/golog"
	"github.com/webview/webview"
	"go.viam.com/rdk/components/camera"
	"go.viam.com/rdk/rimage"
	robotimpl "go.viam.com/rdk/robot/impl"
	"go.viam.com/rdk/services/vision"
	"go.viam.com/rdk/vision/objectdetection"

	// registers all cameras.
	_ "go.viam.com/rdk/components/camera/register"
	// registers the vision service
	_ "go.viam.com/rdk/services/vision/register"
	// registers the mlmodel service
	_ "go.viam.com/rdk/services/mlmodel/register"
)

const (
	pathHere = "/full/path/to/vision-service-examples/go/"
	saveTo   = "output.jpg"
)

func main() {
	// Setup robot client
	logger := golog.NewDevelopmentLogger("example")

	// if you want to create the robot directly from a JSON config
	r, err := robotimpl.RobotFromConfigPath(context.Background(), "robot_config.json", logger)
	// if you want to read the robot from the app
	// r, err := robotFromConnection(logger)
	if err != nil {
		logger.Fatalf("cannot create robot: %v", err)
	}
	defer r.Close(context.Background())

	// Print available resources
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
	// grab Viam's vision service that already has the TF-Lite model for object detection
	myDetector, err := vision.FromRobot(r, "myDetector")
	if err != nil {
		logger.Fatalf("cannot get vision service: %v", err)
	}

	// Do not display any detection with confidence < confThreshold
	confThreshold := 0.6
	for {
		// get image
		img, release, err := camStream.Next(context.Background())
		if err != nil {
			logger.Fatalf("cannot get image: %v", err)
		}
		defer release()

		// get detection bounding boxes
		detections, err := myDetector.Detections(context.Background(), img, nil)
		if err != nil {
			logger.Errorf("detection error: %v", err)
			continue
		}
		// get the detections that appear above a certain confidence (0.6 here)
		labels := make([]string, 0, 25)
		filtered := make([]objectdetection.Detection, 0, len(detections))
		for _, d := range detections {
			if d.Score() > confThreshold {
				filtered = append(filtered, d)
				labels = append(labels, d.Label())
			}
		}
		logger.Infof("found these objects in image: %v", labels)

		// draw the filtered detections onto the image
		saveMe, err := objectdetection.Overlay(img, filtered)
		if err != nil {
			logger.Errorf("could not overlay image")
		}

		// save image locally and display if interesting
		rimage.SaveImage(saveMe, saveTo)
		if len(labels) > 0 {
			displayImage(saveMe) // once this is called, you're done.
		}

	}

}

// displayImage will display the image stored in pathHere+saveTo
func displayImage(img image.Image) {
	webView := webview.New(true)
	defer webView.Destroy()
	webView.Navigate("file://" + pathHere + saveTo)
	webView.SetSize(img.Bounds().Dx()+100, img.Bounds().Dy()+100, webview.HintFixed)
	webView.Navigate("file://" + pathHere + saveTo)
	webView.Run()
}
