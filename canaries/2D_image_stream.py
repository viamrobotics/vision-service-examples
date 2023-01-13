import asyncio

import cv2
import datetime
import numpy as np

from PIL import ImageDraw
from collections import deque
from viam.components.camera import Camera
from viam.components.types import CameraMimeType
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

import logging


async def connect():
    logging.info("connecting to robot client")
    creds = Credentials(
        type='robot-location-secret',
        payload='69h68573npk80j95il8tvbl7t1zqyzleukdipvd7y58te1k5')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('holy-sun-main.h78a7zlqox.viam.cloud', opts)


async def main():
    robot = await connect()
    logging.info("finished connecting to robot client")

    cam_name = "cam"
    cam = Camera.from_robot(robot, cam_name)
    logging.info(f"found camera {cam_name}")

    try:
        llist = deque()

        def get_frames_per_sec():
            one_sec_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
            # evict datetimes greater than one sec ago, i.e., datetimes smaller than now()-one_sec_ago
            while llist[0] < one_sec_ago:
                llist.popleft()
            return len(llist)

        logging.info("displaying window")
        while True:
            await cam.get_image(CameraMimeType.JPEG)
            llist.append(datetime.datetime.now())
            fps = get_frames_per_sec()
            logging.info(f"fps={fps}")
    finally:
        logging.info("closing robot")
        await robot.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
