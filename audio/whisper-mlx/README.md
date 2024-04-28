# Whisper MLX Extractor

> This version uses Apple's MLX so it's extremely fast on M series Macs

This extractor converts extracts transcriptions from audio. The entire text and
chunks with timestamps are represented as metadata of the content.

Content[Audio] -> Content[Empty] + Features[JSON metadata of transcription]

## Usage
Try out the extractor. Download your favorite audio podcast which has a lot of speech. 
```
indexify-extractor run-local whisper-mlx.whisper_extractor:WhisperExtractor  --file twiml-ai-podcast.mp3
```
