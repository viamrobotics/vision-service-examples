import asyncio

import cv2
import datetime
import numpy as np
import sys

from PIL import ImageDraw
from collections import deque
from viam.components.camera import Camera
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera.client import CameraMimeType

import logging
import requests
import os

has_webhook = False
if len(sys.argv) > 2:
    url = sys.argv[2]
    has_webhook = True
arg = int(sys.argv[1])

screen_res = 1920, 1080
scale_width = screen_res[0] / 425
scale_height = screen_res[1] / 480
scale = min(scale_width, scale_height)
#resized window width and height
window_width = int(425 * scale)
window_height = int(480 * scale)

async def connect():
    logging.info("connecting to robot client")
    creds = Credentials(
        type='robot-location-secret',
        payload='gv3b40fw2ii1a0g5dfhfu7i085f7rfj8jm2oh692znd0sedj')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('2d-stream-main.i2z4laurah.viam.cloud', opts)


async def close_robot(robot):
    if robot:
        logging.info("closing robot")
        await robot.close()
        logging.info("robot closed")


def get_frames_per_sec(ordered_frames):
    one_sec_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
    # evict datetimes greater than one sec ago, i.e., datetimes smaller than now()-one_sec_ago
    while ordered_frames[0] < one_sec_ago:
        ordered_frames.popleft()
    return len(ordered_frames)

async def detection_stream(robot, llist2):
    transform_cam_name = "transform"
    transform = Camera.from_robot(robot, transform_cam_name)
    logging.info(f"found camera {transform_cam_name}")
    while True:
        # This is to stop this script just before the start of the next hour.
        current_min = int(datetime.datetime.now().strftime("%M"))
        if current_min == 59:
            await close_robot(robot)
            return
        detect_img = await transform.get_image(CameraMimeType.JPEG) # default is PNG, JPEG is faster
        llist2.append(datetime.datetime.now())

        draw = ImageDraw.Draw(detect_img)
        draw.rectangle((0, 0, 75, 25), outline='black')
        fps = get_frames_per_sec(llist2)
        draw.text(xy=(18, 7.5), text=f'{fps} FPS', fill='white')

        pix = cv2.cvtColor(np.array(detect_img, dtype=np.uint8), cv2.COLOR_RGB2BGR)

        window_name = 'Detections'
        cv2.namedWindow(window_name, cv2.WND_PROP_VISIBLE)
        if arg == 2:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else: 
            pix = pix[0:480, 0:425]
            cv2.resizeWindow(window_name, window_width, window_height)
            cv2.moveWindow(window_name, window_width, 0)
        cv2.imshow(window_name, pix)
        cv2.waitKey(1)
    return

async def image_stream(robot, llist1):
    cam_name = "standard_camera"
    cam = Camera.from_robot(robot, cam_name)
    logging.info(f"found camera {cam_name}")
    while True:
        # This is to stop this script just before the start of the next hour.
        current_min = int(datetime.datetime.now().strftime("%M"))
        if current_min == 59:
            await close_robot(robot)
            return
        pil_img = await cam.get_image()
        llist1.append(datetime.datetime.now())

        draw = ImageDraw.Draw(pil_img)
        draw.rectangle((0, 0, 75, 25), outline='black')
        fps = get_frames_per_sec(llist1)
        draw.text(xy=(18, 7.5), text=f'{fps} FPS', fill='white')

        open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        window_name = '2D'
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        if arg == 1:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            open_cv_image = open_cv_image[0:480, 0:425]
            cv2.resizeWindow(window_name, window_width, window_height)
            cv2.moveWindow(window_name, 0, 0)
        cv2.imshow(window_name, open_cv_image)
        cv2.waitKey(1)
    return

async def main():
    robot = None
    llist1 = deque()
    llist2 = deque()
    try:
        robot = await connect()
        logging.info("finished connecting to robot client")       

        if arg == 1:
            await image_stream(robot, llist1)
        elif arg == 2:
            await detection_stream(robot, llist2)
        elif arg == 3:
            task1 = asyncio.create_task(image_stream(robot, llist1))
            task2 = asyncio.create_task(detection_stream(robot, llist2))
            await task1
            await task2
        else:
            logging.info("unaccepted argument")

    except Exception as e:
        logging.info(f"caught exception '{e}'")
        if has_webhook:
            body = {"text": f'{e}'}
            res = requests.post(url, json=body)
        await close_robot(robot)
        logging.info("exiting with status 1")
        exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        filename='/tmp/canary_logs.txt',
        encoding='utf-8',
        level=logging.INFO,
        filemode='w',
        force=True
    )

    now = lambda: datetime.datetime.now().strftime('%H:%M:%S')
    logging.info(f"start time {now()}")
    try:
        asyncio.run(main())
    finally:
        logging.info(f"end time {now()}")

