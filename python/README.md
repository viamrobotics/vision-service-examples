In this example, it assumes you have an RGB camera called `cam1`, and an object detection model called `find_objects`.

In your robot config, make sure you have the following configured

In CONFIG -> Components, configure your webcam
```
{ "name": "cam1",
  "type": "camera",
  "model": "webcam"
}
```

In CONFIG -> Services, configure your object detection model
```
{
  "name": "vis_service",
  "type": "vision",
  "attributes": {
      "register_models": [
        {
          "parameters": {
            "model_path": "/full/path/to/vision-service-examples/data/effdet0.tflite",
            "label_path": "/full/path/to/vision-service-examples/data/effdetlabels.txt",
            "num_threads": 1
          },
          "name": "find_objects",
          "type": "tflite_detector"
        }
     ]
  }
}
```
