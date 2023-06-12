import asyncio,os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.vision import VisionClient
from viam.components.camera import Camera
import cv2
import numpy as np

##on command line run:
##export ROBOT_SECRET=your_robot_secret from app.viam.com
##export ROBOT_ADDRESS=your_robot_address from app.viam.com

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=os.getenv('ROBOT_SECRET'))
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(os.getenv('ROBOT_ADDRESS'), opts)

async def main():

    robot = await connect()
    # grab camera from the robot
    cam1 = Camera.from_robot(robot, "web_cam")
    # grab Viam's vision service for the detector
    my_detector = VisionClient.from_robot(robot, "vision_svc")

    cv2.namedWindow('object_detect', cv2.WINDOW_NORMAL)
    # loop forever:  find objects using Viam Vision, and draw boxes aroung them using openCV
    try:
        while(True):
            print("hi")
            img = await cam1.get_image()
            detections = await my_detector.get_detections(img)
            print(detections)
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
    finally:
        print("closing robot")
        await robot.close()
        print("robot closed")
        

if __name__ == '__main__':
    asyncio.run(main())

