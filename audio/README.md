# Audio Extractors

To begin utilizing these extractors install the indexify-extractor CLI.

```bash
pip install indexify-extractor-sdk
```

## Download and Run
```bash
indexify-extractor download <download-link>
indexify-extractor join-server
```

| Name                | Download link                   | Extractor Module Name                           |
|---------------------|---------------------------------|-------------------------------------------------|
| whisper-asr         | hub://audio/whisper-asr         | whisper_extractor:WhisperExtractor              |
| whisper-diarization | hub://audio/whisper-diarization | whisper_diarization:WhisperDiarizationExtractor |
| asrdiarization      | hub://audio/asrdiarization      | asr_extractor:ASRExtractor                      |
