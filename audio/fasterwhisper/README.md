# Faster Whisper Extractor

This extractor converts extracts transcriptions from audio. The entire text  with timestamps are represented as metadata of the content.

Content[Audio] -> Content[Empty] + Features[JSON metadata of transcription]

## Usage
Try out the extractor. Download your favorite audio podcast which has a lot of speech. 
```
cd faster_whisper
indexify extractor extract --file twiml-ai-podcast.mp3
```

## Container
* The container is not published yet. *
```
docker run  -it diptanu/fasterwhisper extractor extract --file all-in-e154.mp3
```
