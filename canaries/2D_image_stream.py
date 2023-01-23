import asyncio
import os
import time

import cv2
import datetime
import numpy as np

from PIL import ImageDraw
from collections import deque
from viam.components.camera import Camera
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

import logging


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


def close_robot(robot):
    if robot:
        logging.info("closing robot")
        robot.close()
        logging.info("robot closed")


def get_frames_per_sec(ordered_frames):
    one_sec_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
    # evict datetimes greater than one sec ago, i.e., datetimes smaller than now()-one_sec_ago
    while ordered_frames[0] < one_sec_ago:
        ordered_frames.popleft()
    return len(ordered_frames)

def restart_server():
    logging.info("restarting the viam-server...")
    os.system("systemctl restart viam-server")
    time.sleep(30)  # give the viam-server time to restart
    logging.info("viam-server up")

async def main():
    robot = None
    llist = deque()
    attempts = 3  # how many times we should retry before failing
    for _ in range(attempts):
        try:
            robot = await connect()
            logging.info("finished connecting to robot client")

            cam_name = "standard_camera"
            cam = Camera.from_robot(robot, cam_name)
            logging.info(f"found camera {cam_name}")

            logging.info("displaying window")
            while True:
                # This is to stop this script just before the start of the next hour.
                current_min = int(datetime.datetime.now().strftime("%M"))
                if current_min == 59:
                    close_robot(robot)
                    return

                pil_img = await cam.get_image()
                llist.append(datetime.datetime.now())

                draw = ImageDraw.Draw(pil_img)
                draw.rectangle((0, 0, 75, 25), outline='black')
                fps = get_frames_per_sec(llist)
                draw.text(xy=(18, 7.5), text=f'{fps} FPS', fill='white')

                open_cv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                window_name = '2D'
                cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(window_name, open_cv_image)
                cv2.waitKey(1)
        except Exception as e:
            logging.info(f"caught exception '{e}'")
            close_robot(robot)
            restart_server()
            continue
    logging.info(f"cannot get image. {attempts} attempts tried and failed")


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
