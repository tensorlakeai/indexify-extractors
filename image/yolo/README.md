# YOLO Image Extractor

The YOLO Image Extractor is a Python-based tool that uses the YOLO (You Only Look Once) model for object detection in images. It's designed to work with the Indexify extractor SDK, providing a simple interface for detecting objects in images and returning their bounding boxes, class names, and confidence scores.

## Features

- Object detection using YOLO model
- Configurable model selection, confidence threshold, and IoU threshold
- Supports JPEG and PNG image formats
- Returns detected objects as JSON with bounding boxes, class names, and confidence scores

## Usage

Here's a basic example of how to use the YOLO Image Extractor:

```python
from yolo_extractor import YoloExtractor, YoloExtractorConfig
from indexify_extractor_sdk import Content

# Load an image
with open("path/to/your/image.jpg", "rb") as f:
    image_data = f.read()

# Create input content
input_content = Content(content_type="image/jpeg", data=image_data)

# Configure the extractor
config = YoloExtractorConfig(
    model_name='yolov8n.pt',
    conf=0.25,
    iou=0.7
)

# Create and run the extractor
extractor = YoloExtractor()
results = extractor.extract(input_content, params=config)

# Process the results
for result in results:
    detection = json.loads(result.data)
    confidence = result.features[0].metadata['score']
    print(f"Detected: {detection['class']}")
    print(f"Bounding Box: {detection['bbox']}")
    print(f"Confidence: {confidence}")
    print("---")
```

## Example Input/Output

### Input

The input is an image file (JPEG or PNG) containing objects to be detected. For example, let's say we have an image `street_scene.jpg` with cars and people.

### Output

The extractor will return a list of `Content` objects, each representing a detected object. Here's an example of what the output might look like:

```python
[
    Content(
        content_type="application/json",
        data='{"bbox": [100, 200, 300, 400], "class": "car"}',
        features=[Feature(metadata={"score": 0.92})]
    ),
    Content(
        content_type="application/json",
        data='{"bbox": [50, 150, 100, 250], "class": "person"}',
        features=[Feature(metadata={"score": 0.87})]
    ),
    Content(
        content_type="application/json",
        data='{"bbox": [400, 300, 600, 500], "class": "car"}',
        features=[Feature(metadata={"score": 0.95})]
    )
]
```

Each detection includes:
- The class of the detected object
- The bounding box coordinates [x1, y1, x2, y2]
- The confidence score of the detection

## Configuration

You can configure the YOLO Image Extractor using the `YoloExtractorConfig` class:

- `model_name`: The name or path of the YOLO model to use (default: 'yolov8n.pt')
- `conf`: Confidence threshold for detections (default: 0.25)
- `iou`: IoU (Intersection over Union) threshold for NMS (default: 0.7)
