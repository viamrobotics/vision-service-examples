import argparse
import asyncio
import os
from utils import Fps
import cv2
import numpy as np
import open3d as o3d
from enum import Enum
from screeninfo import get_monitors

from PIL import Image, ImageDraw
from viam.components.camera import Camera
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.errors import ResourceNotFoundError


class SourceType(Enum):
    WEBCAM='webcam'
    PCD='pcd' # PCD must come before REALSENSE_COLOR and REALSENSE_DEPTH
              # because both realsense:color and realsense:depth will be
              # valid cameras when reading PCD data, and these values
              # are checked sequentially for their presence on the robot
    REALSENSE_COLOR='realsense:color'
    REALSENSE_DEPTH='realsense:depth'


parser = argparse.ArgumentParser()

parser.add_argument('--secret', type=str, required=True, help='the credential')
parser.add_argument('--address', type=str, required=True, help='address of the robot (IP address, URL, etc.)')

args = parser.parse_args()

monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=args.secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(args.address, opts)

async def close_robot(robot):
    if robot:
        await robot.close()

async def stream_2D(cam):
    fps = Fps()
    window_name = 'Stream 2D'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        pil_img = await cam.get_image()
        fps.record()

        draw = ImageDraw.Draw(pil_img)
        draw.rectangle((0, 0, 275, 30), outline='black')
        draw.text(xy=(18, 2), text=f'{fps.get()} FPS', fill='white')
        
        curr_test_name = os.environ['curr_test_name']
        draw.text(xy=(18, 15), text=curr_test_name, fill='white')

        opencv_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Resize image to fit screen
        image_height, image_width, _ = opencv_image.shape
        new_width = screen_width
        new_height = screen_height
        if image_width > image_height:
            new_height = int(image_height/image_width * screen_width)
        else:
            new_width = int(image_width/image_height * screen_height)
        resized_image = cv2.resize(opencv_image, (new_width,new_height))

        cv2.imshow(window_name, resized_image)
        cv2.waitKey(1)

async def stream_3D(cam):
    point_cloud_path = '/tmp/pointcloud_data.pcd'
    fps_image_path = '/tmp/fps_text.png'
    fps = Fps()
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.set_full_screen(True)
    while True:
        data, _ = await cam.get_point_cloud()
        fps.record()

        with open(point_cloud_path, 'wb') as f:
            f.write(data)
        
        pcd = o3d.io.read_point_cloud(point_cloud_path)
        vis.clear_geometries()

        vis.add_geometry(pcd)
        fps_img = Image.new('RGB', (screen_width,screen_height), color=(255,255,255))
        draw = ImageDraw.Draw(fps_img)
        draw.text(xy=(0,0), text=f'{fps.get()} FPS', fill='black')
        curr_test_name = os.environ['curr_test_name']
        draw.text(xy=(0, 10), text=curr_test_name, fill='black')
        fps_img.save(fps_image_path)

        im = o3d.io.read_image(fps_image_path)
        vis.add_geometry(im)

        vis.poll_events()
        vis.update_renderer()

async def stream(robot, source_type):
    cam = Camera.from_robot(robot, source_type.value)
    if source_type in [SourceType.WEBCAM, SourceType.REALSENSE_COLOR, SourceType.REALSENSE_DEPTH]:
        await stream_2D(cam)
    elif source_type == SourceType.PCD:
        await stream_3D(cam)

async def determine_source_type(robot):
    # Try each source type and see which one works
    for source_type in SourceType:
        try:
            cam = Camera.from_robot(robot, source_type.value)
            return source_type
        except ResourceNotFoundError as e:
            continue

async def main():
    robot = None
    exit_status = 0
    robot = await connect()
    source_type = await determine_source_type(robot)
    await stream(robot, source_type)
    await close_robot(robot)
    exit(exit_status)

if __name__ == '__main__':
    asyncio.run(main())