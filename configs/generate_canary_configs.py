import json

num_spaces_for_indent = 2
configs_path = './canary-main-configs/'
logitech_video_path = 'usb-046d_C922_Pro_Stream_Webcam_85809C6F-video-index0'

# Tests 1-9
def make_logitech_yuyv_tests():
    for width, height in [(640, 480),
                          (800, 448),
                          (864, 480),
                          (960, 720),
                          (1024, 576),
                          (1280, 720),
                          (1600, 896),
                          (1920, 1080)]:
        config = {
            'components': [
                {
                    'name': 'webcam',
                    'type': 'camera',
                    'model': 'webcam',
                    'attributes': {
                        'width_px': width,
                        'height_px': height,
                        'format': 'MJPEG',
                        'video_path': logitech_video_path
                    }
                }
            ]
        }
        with open(f'{configs_path}logitech-yuyv-{width}x{height}.json', 'w') as f:
            f.write(json.dumps(config, indent=num_spaces_for_indent))

# Tests 10, 19
def make_logitech_with_detections_test(format):
    width = 1280
    height = 720
    config = {
        'packages': [
            {
                'name': 'effdet0',
                'version': 'latest',
                'package': '3a2e76e2-3fa5-40a6-83df-ee3cff3747f0/effdet0'
            }
        ],
        'components': [
            {
                'type': 'camera',
                'model': 'webcam',
                'attributes': {
                    'width_px': 1280,
                    'height_px': 720,
                    'format': format,
                    'video_path': 'usb-046d_C922_Pro_Stream_Webcam_85809C6F-video-index0'
                },
                'name': 'sourceCam',
                'depends_on': []
            },
            {
                'attributes': {
                    'pipeline': [
                        {
                            'attributes': {
                                'detector_name': 'detector',
                                'confidence_threshold': 0.3
                            },
                            'type': 'detections'
                        }
                    ],
                    'source': 'sourceCam'
                },
                'depends_on': [],
                'name': 'webcam',
                'type': 'camera',
                'model': 'transform'
            }
        ],
        'services': [
            {
                'name': 'detector',
                'type': 'vision',
                'model': 'mlmodel',
                'attributes': {
                    'mlmodel_name': 'effdet'
                }
            },
            {
                'name': 'effdet',
                'type': 'mlmodel',
                'model': 'tflite_cpu',
                'attributes': {
                    'model_path': '${packages.effdet0}/effdet0.tflite',
                    'label_path': '${packages.effdet0}/labels.txt',
                    'num_threads': 1
                }
            }
        ]
    }
    with open(f'{configs_path}logitech-{format.lower()}-{width}x{height}-detections.json', 'w') as f:
        f.write(json.dumps(config, indent=num_spaces_for_indent))

# Tests 11-18
def make_logitech_mjpeg_tests():
    for width, height in [(640, 480),
                          (800, 448),
                          (800, 600),
                          (960, 720),
                          (1024, 576),
                          (1280, 720),
                          (1600, 896),
                          (1920, 1080)]:
        config = {
            'components': [
                {
                    'name': 'webcam',
                    'type': 'camera',
                    'model': 'webcam',
                    'attributes': {
                        'video_path': logitech_video_path,
                        'format': 'MJPEG',
                        'width_px': width,
                        'height_px': height
                    }
                }
            ]
        }
        with open(f'{configs_path}logitech-mjpeg-{width}x{height}.json', 'w') as f:
            f.write(json.dumps(config, indent=num_spaces_for_indent))

# Test 20
def make_emeet_remote_test():
    config = {
      'components': [],
      'remotes': [
        {
            'name': 'canary-remote-main',
            'address': 'canary-remote-main.lm93zdrt5p.viam.cloud',
            'secret': '3pfh6vpvvup4h7071d1x41q99h2oqhlp89lwdanq3zn0oy3f'
        }
      ]
    }
    with open(f'{configs_path}emeet.json', 'w') as f:
        f.write(json.dumps(config, indent=num_spaces_for_indent))

# Tests 21-24
def make_realsense_yuyv_tests():
    for width, height in [(640, 480),
                          (848, 480),
                          (1280, 720),
                          (1280, 800)]:
        config = {
            'remotes': [
                {
                    'name': 'realsense',
                    'address': '127.0.0.1:8085'
                }
            ],
            'processes': [
                {
                    'id': 'realsense-server',
                    'name': '/usr/local/bin/intelrealgrpcserver',
                    'log': True,
                    'args': [
                        '8085',
                        f'{width}',
                        f'{height}',
                        '0',
                        '0',
                        '--disable-depth'
                    ]
                }
            ]
        }
        with open(f'{configs_path}realsense-yuyv-{width}x{height}.json', 'w') as f:
            f.write(json.dumps(config, indent=num_spaces_for_indent))

# Tests 25-27
def make_realsense_z16_tests():
    for width, height in [(640, 480),
                          (848, 480),
                          (1280, 720)]:
        config = {
            'remotes': [
                {
                    'name': 'realsense',
                    'address': '127.0.0.1:8085'
                }
            ],
            'processes': [
                {
                    'id': 'realsense-server',
                    'name': '/usr/local/bin/intelrealgrpcserver',
                    'log': True,
                    'args': [
                        '8085',
                        '0',
                        '0',
                        f'{width}',
                        f'{height}',
                        '--disable-color'
                    ]
                }
            ]
        }
        with open(f'{configs_path}realsense-z16-{width}x{height}.json', 'w') as f:
            f.write(json.dumps(config, indent=num_spaces_for_indent))

# Tests 28-30
def make_realsense_pcd_tests():
    for width, height in [(640, 480),
                          (848, 480),
                          (1280, 720)]:
        config = {
            'components': [
                {
                    'name': 'pcd',
                    'type': 'camera',
                    'model': 'join_color_depth',
                    'attributes': {
                        'color_camera_name': 'realsense:color',
                        'depth_camera_name': 'realsense:depth',
                        'intrinsic_parameters': {
                            'width_px': 480,
                            'height_px': 640,
                            'ppx': 320.215759,
                            'ppy': 239.543106,
                            'fx': 608.71105,
                            'fy': 609.39044
                        },
                        'output_image_type': 'color'
                    }
                }
            ],
            'remotes': [
                {
                    'name': 'realsense',
                    'address': '127.0.0.1:8085'
                }
            ],
            'processes': [
                {
                    'id': 'realsense-server',
                    'name': '/usr/local/bin/intelrealgrpcserver',
                    'log': True,
                    'args': [
                        '8085',
                        f'{width}',
                        f'{height}',
                        f'{width}',
                        f'{height}'
                    ]
                }
            ]
        }
        with open(f'{configs_path}realsense-pcd-{width}x{height}.json', 'w') as f:
            f.write(json.dumps(config, indent=num_spaces_for_indent))

def main():
    make_logitech_yuyv_tests()
    make_logitech_with_detections_test(format='YUYV')
    make_logitech_mjpeg_tests()
    make_logitech_with_detections_test(format='MJPEG')
    make_emeet_remote_test()
    make_realsense_yuyv_tests()
    make_realsense_z16_tests()
    make_realsense_pcd_tests()

if __name__ == '__main__':
    main()