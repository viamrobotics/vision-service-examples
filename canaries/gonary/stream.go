package main

import (
	"context"
	"flag"
	"fmt"
	"image"
	"image/color"
	"time"

	"gocv.io/x/gocv"

	"github.com/edaniels/golog"
	"go.viam.com/rdk/components/camera"
	"go.viam.com/rdk/robot/client"
	"go.viam.com/rdk/utils"
	"go.viam.com/utils/rpc"

	cutils "go.viam.com/canary/utils"
)

// stream2D streams the 2D camera feed from the robot.
func stream2D(cam camera.Camera, logger golog.Logger, resolutionWidth, resolutionHeight, coordinatesX, coordinatesY int) {
	// Create window viewer.
	window := gocv.NewWindow("2D")
	window.ResizeWindow(resolutionWidth, resolutionHeight)
	window.MoveWindow(coordinatesX, coordinatesY)
	defer window.Close()

	// Create camera stream.
	camStream, err := cam.Stream(context.Background())
	if err != nil {
		logger.Error(err)
	}

	// Create FPS struct
	fps := cutils.Fps{
		OrderedFrames: make([]time.Time, 0),
		PrevGet:       time.Now(),
		CachedFps:     0,
	}

	// Main image loop
	for {
		img, release, err := camStream.Next(context.Background())
		if err != nil {
			logger.Fatalf("cannot get image: %v", err)
			continue
		}
		defer release()

		// Record FPS
		fps.Record()

		mat, err := gocv.ImageToMatRGB(img)
		if err != nil {
			logger.Infof("cannot convert image to mat: %v", err)
			continue
		}

		// Draw FPS on image.
		gocv.PutText(&mat, fmt.Sprintf("%d FPS", fps.Get()), image.Pt(10, 20), gocv.FontHersheyPlain, 1.2, color.RGBA{255, 255, 255, 255}, 2)

		window.IMShow(mat)
		window.WaitKey(1)
	}
}

func main() {
	// Command line flags
	payload := flag.String("payload", "", "the credential")
	address := flag.String("address", "", "address of the robot (IP address, URL, etc.)")
	resolutionWidth := flag.Int("resolution-width", 0, "the width of the display window")
	resolutionHeight := flag.Int("resolution-height", 0, "the height of the display window")
	coordinatesX := flag.Int("coordinates-x", 0, "the x-coordinate of the display window")
	coordinatesY := flag.Int("coordinates-y", 0, "the y-coordinate of the display window")
	cameraName := flag.String("cam", "", "the name of the camera")
	webhook := flag.String("webhook", "", "the webhook to send logging info")

	flag.Parse()

	fmt.Println("payload:", *payload)
	fmt.Println("address:", *address)
	fmt.Println("resolution:", *resolutionWidth, *resolutionHeight)
	fmt.Println("coordinates:", *coordinatesX, *coordinatesY)
	fmt.Println("cam:", *cameraName)
	fmt.Println("webhook:", *webhook)

	// Setup robot client
	logger := golog.NewDevelopmentLogger("client")
	robot, err := client.New(
		context.Background(),
		*address,
		logger,
		client.WithDialOptions(rpc.WithCredentials(rpc.Credentials{
			Type:    utils.CredentialsTypeRobotLocationSecret,
			Payload: *payload,
		})),
	)
	if err != nil {
		logger.Fatal(err)
	}
	defer robot.Close(context.Background())

	// Extract camera from robot
	cam, err := camera.FromRobot(robot, "cam1")
	if err != nil {
		logger.Error(err)
	}
	camProps, err := cam.Properties(context.Background())
	if err != nil {
		logger.Error(err)
	}
	logger.Infof("cam1 Properties return value: %v", camProps)
	logger.Info("Resources:")
	logger.Info(robot.ResourceNames())

	// Stream 2D camera feed
	stream2D(cam, logger, *resolutionWidth, *resolutionHeight, *coordinatesX, *coordinatesY)

}
