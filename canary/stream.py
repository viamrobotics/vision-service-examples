import re
import argparse
import asyncio
from enum import Enum
from utils import Fps
import cv2
import numpy as np
import open3d as o3d
from screeninfo import get_monitors

from PIL import Image, ImageDraw
from viam.components.camera import Camera
from viam.robot.client import RobotClient
from viam.rpc.dial import DialOptions


class SourceType(Enum):
    LOGITECH='logitech'
    REALSENSE='realsense'
    REMOTE='remote'

class FormatType(Enum):
    YUYV='yuyv'
    MJPEG='mjpeg'
    PCD='pcd'
    Z16='z16'

parser = argparse.ArgumentParser()
parser.add_argument('--config_name', type=str, required=True, help='the config name')
args = parser.parse_args()

monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

async def connect():
    opts = RobotClient.Options(
      refresh_interval=0,
      dial_options=DialOptions(insecure=True)
    )
    return await RobotClient.at_address('localhost:8080', opts)

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
        draw.text(xy=(18, 15), text=args.config_name, fill='white')

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
        draw.text(xy=(0, 10), text=args.config_name, fill='black')
        fps_img.save(fps_image_path)

        im = o3d.io.read_image(fps_image_path)
        vis.add_geometry(im)

        vis.poll_events()
        vis.update_renderer()

async def stream(robot):
    # Split on - and .
    tokens = re.split('-|\.', args.config_name)
    source_type = SourceType(tokens[0])
    camera_name = None
    stream_func = None
    if source_type == SourceType.REMOTE:
        camera_name = 'canary-remote-main:webcam'
        stream_func = stream_2D
    if source_type == SourceType.LOGITECH:
        camera_name = 'webcam'
        stream_func = stream_2D
    elif source_type == SourceType.REALSENSE:
        format_type = FormatType(tokens[1])
        if format_type == FormatType.PCD:
            camera_name = 'pcd'
            stream_func = stream_3D
        elif format_type == FormatType.YUYV:
            camera_name = 'realsense:color'
            stream_func = stream_2D
        elif format_type == FormatType.Z16:
            camera_name = 'realsense_depth'
            stream_func = stream_2D

    cam = Camera.from_robot(robot, camera_name)
    await stream_func(cam)

async def main():
    robot = None
    exit_status = 0
    robot = await connect()
    await stream(robot)
    await close_robot(robot)
    exit(exit_status)

if __name__ == '__main__':
    asyncio.run(main())