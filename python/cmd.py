import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionServiceClient
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
    # establish a connection to the robot client
    robot = await connect()
    # grab camera from the robot
    cam1 = Camera.from_robot(robot, "cam1")
    # grab your vision service, here named "myDetector", which has the TFLite detector already registered
    myDetector = VisionServiceClient.from_robot(robot, "myDetector")
    # make a display window
    cv2.namedWindow('object_detect', cv2.WINDOW_NORMAL)
    # loop forever:  find objects using Viam Vision, and draw boxes aroung them using openCV
    while(True):
        img = await cam1.get_image() # default is JPEG
        detections = await myDetector.get_detections(img)
        # turn image into numpy array
        pix = np.array(img, dtype=np.uint8)
        pix = cv2.cvtColor(pix, cv2.COLOR_RGB2BGR)
        # put boxes around objects with enough confidence (> 0.6)
        conf = 0.6
        for d in detections:
            if d.confidence > conf:
                cv2.rectangle(pix, (d.x_min, d.y_min), (d.x_max, d.y_max), (0, 0, 255), 3)
        cv2.imshow('object_detect',pix)
        cv2.waitKey(1)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
