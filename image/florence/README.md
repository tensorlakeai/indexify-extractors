# FlorenceImageExtractor

FlorenceImageExtractor is a powerful image analysis tool leveraging the Microsoft Florence-2 large vision-language model. It performs a wide range of image understanding tasks, from simple captioning to complex visual reasoning.

## Key Features

- Comprehensive image analysis capabilities
- Flexible configuration
- Support for JPEG, PNG, and GIF formats
- Seamless integration with Indexify framework

## Supported Tasks

1. Image Captioning
2. Object Detection
3. Dense Region Captioning
4. Region Proposal
5. Caption-to-Phrase Grounding
6. Referring Expression Segmentation
7. Region-to-Segmentation
8. Open Vocabulary Detection
9. Region-to-Category Classification
10. Region-to-Description
11. Optical Character Recognition (OCR)

## Task Prompts

Use these prompts to specify the desired analysis:

- `<CAPTION>`: Brief image caption
- `<DETAILED_CAPTION>`: Comprehensive caption
- `<OD>`: Object detection
- `<DENSE_REGION_CAPTION>`: Captions for image regions
- `<REGION_PROPOSAL>`: Suggest regions of interest
- `<CAPTION_TO_PHRASE_GROUNDING>`: Ground caption phrases to image regions
- `<REFERRING_EXPRESSION_SEGMENTATION>`: Segment image based on description
- `<REGION_TO_SEGMENTATION>`: Convert region to segmentation mask
- `<OPEN_VOCABULARY_DETECTION>`: Detect objects with open vocabulary
- `<REGION_TO_CATEGORY>`: Classify region into category
- `<REGION_TO_DESCRIPTION>`: Describe specific region
- `<OCR>`: Perform OCR
- `<OCR_WITH_REGION>`: OCR with region information

## Examples

### Image Captioning

Input:
```python
config = FlorenceImageExtractorConfig(task_prompt='<CAPTION>')
results = extractor.extract(image_content, params=config)
```

Output:
```python
[Content(data=b'A green Volkswagen Beetle parked in front of a yellow building.', mime_type='text/plain')]
```

### Object Detection

Input:
```python
config = FlorenceImageExtractorConfig(task_prompt='<OD>')
results = extractor.extract(image_content, params=config)
```

Output:
```python
[Content(data=b"{'<OD>': {'bboxes': [[33.599998474121094, 159.59999084472656, 596.7999877929688, 371.7599792480469], [454.0799865722656, 96.23999786376953, 580.7999877929688, 261.8399963378906], [224.95999145507812, 86.15999603271484, 333.7599792480469, 164.39999389648438], [449.5999755859375, 276.239990234375, 554.5599975585938, 370.3199768066406], [91.19999694824219, 280.0799865722656, 198.0800018310547, 370.3199768066406]], 'labels': ['car', 'door', 'door', 'wheel', 'wheel']}}", mime_type='text/plain')]
```

## Performance and Scalability

- State-of-the-art performance in various image analysis tasks
- Handles high-resolution images and batch processing
- Optimal performance with CUDA-enabled GPU

## Limitations

- Accuracy may vary with image complexity and task
- Processing time can be significant for complex tasks
- Performance depends on Florence-2 model's training data

FlorenceImageExtractor provides a comprehensive suite of image analysis capabilities, making it valuable for a wide range of computer vision and AI applications.