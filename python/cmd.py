import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionServiceClient
from viam.services.vision import VisModelConfig, VisModelType, Detection
from viam.components.camera import Camera
import numpy as np
import cv2

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='[PUT  IN INFO FROM ROBOT CONNECT TAB ON APP]')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('[INFO FROM ROBOT CONNECT TAB ON APP]', opts)

async def main():
    robot = await connect()
    # grab camera from the robot
    cam1 = Camera.from_robot(robot, "cam1")
    # grab Viam's vision service to add a TF-lite model for person detection
    vision = VisionServiceClient.from_robot(robot)
    params = {
        "model_path": "/full/path/to/vision-service-examples/data/effdet0.tflite", 
        "num_threads": 1,
    }
    findPersonDetector = VisModelConfig(name="object_detect", type=VisModelType("tflite_detector"), parameters=params)
    await vision.add_detector(findPersonDetector)
    # make a display window
    cv2.namedWindow('object_detect', cv2.WINDOW_NORMAL)
    # loop forever,  find the person using Viam Vision, and draw the box using openCV
    while(True):
        img = await cam1.get_image(CameraMimeType.JPEG) # default is PNG, JPEG is faster
        detections = await vision.get_detections(img, "object_detect")
        person_d = None
        # turn image into numpy array
        pix = np.array(img, dtype=np.uint8)
        pix = cv2.cvtColor(pix, cv2.COLOR_RGB2BGR)
        # put boxes around objects with enough confidence
        for d in detections:
            if d.confidence > 0.6:
                cv2.rectangle(pix, (d.x_min, d.y_min), (d.x_max, d.y_max), (0, 0, 255), 3)
        cv2.imshow('object_detect',pix)
        cv2.waitKey(1)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
