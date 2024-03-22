# Scene Frame Extractor

Dissect a video into its individual frames and generate JPEG image content for each extracted frame. Comes with frame frequency and scene detection that can be configured with input parameters.

Input content: video/mp4
Output: jpg image content for each frame

### Input parameters
- max_fps:int (default 60) - can be used if you turn off key_frames, the maximum number of frames to extract per second
- key_frames:bool (default true) - will only extract key frames using histogram comparison for scene detection. This will override max_fps parameter
- key_frames_threshold:float (default 0.8) - the lower the number the less similar the frames have to be in order to trigger a scene detection

