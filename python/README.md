In this example, it assumes you have an RGB camera called `cam1`, and an object detection model called `find_objects`.

In your robot config, make sure you have the following configured

In CONFIG -> Components, configure your webcam
```
{ "name": "cam1",
  "type": "camera",
  "model": "webcam"
}
```

In CONFIG -> Services, add your mlmodel and your object detection vision service
```
{
  "model": "tflite_cpu",
  "attributes": {
    "model_path": "/full/path/to/vision-service-examples/data/effdet0.tflite",
    "label_path": "/full/path/to/vision-service-examples/data/effdetlabels.txt",
    "num_threads": 1
  },
  "name": "EffDet",
  "type": "mlmodel"
},
{
  "depends_on": ["EffDet"],
  "model": "mlmodel",
  "attributes": {
    "mlmodel_name": "EffDet"
  },
  "name": "myDetector",
  "type": "vision"
}
```
