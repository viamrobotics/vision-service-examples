import asyncio

import cv2
import datetime
import numpy as np

from PIL import ImageDraw
from heapq import heappush, heappop
from viam.components.camera import Camera
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions


async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='pem1epjv07fq2cz2z5723gq6ntuyhue5t30boohkiz3iqht4')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('pointcloud-cam2-main.60758fe0f6.viam.cloud', opts)


async def main():
    robot = await connect()
    cam = Camera.from_robot(robot, "standard_camera")
    try:
        heap = []

        def get_frames_per_sec():
            one_sec_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
            # evict datetimes greater than one sec ago, i.e., datetimes smaller than now()-one_sec_ago
            while heap[0] < one_sec_ago:
                heappop(heap)
            return len(heap)

        while True:
            pil_img = await cam.get_image()
            heappush(heap, datetime.datetime.now())

            draw = ImageDraw.Draw(pil_img)
            draw.rectangle((0, 0, 75, 25), outline='black')
            draw.text(xy=(18, 7.5), text=f'{get_frames_per_sec()} FPS', fill='white')

            open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            cv2.imshow('2D', open_cv_image)
            cv2.waitKey(1)
    finally:
        await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
