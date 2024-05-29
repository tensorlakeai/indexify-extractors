This is a high-level diagram of what the extractor looks like under the hood:

![pipeline_schema](pipeline_schema.png)

The implementation of ASR and diarization pipelines is modularized to cater to a wider range of use cases - the diarization pipeline operates on top of ASR outputs, and you can use only the ASR part if diarization is not needed. For diarization, we propose using the [Pyannote model](https://huggingface.co/pyannote/speaker-diarization-3.1), currently a SOTA open source implementation.

We’ll also add speculative decoding as a way to speed up inference. The speedup is achieved by using a smaller and faster model to suggest generations that are validated by the larger model. Learn more about how it works with Whisper specifically in [this great blog post](https://huggingface.co/blog/whisper-speculative-decoding).

Speculative decoding comes with restrictions:

- at least the decoder part of an assistant model should have the same architecture as that of the main model
- the batch size much be 1

Make sure to take the above into account. Depending on your production use case, supporting larger batches can be faster than speculative decoding. If you don't want to use an assistant model, just keep the `assistant_model` in the configuration as `None`.

If you do use an assistant model, a great choice for Whisper is a [distilled version](https://huggingface.co/distil-whisper).

### Example Notebook - [Open in Google Colab](https://colab.research.google.com/drive/1aW6DdAkxTQWZcCe1fS0QCVZ6GeQFji2S?usp=sharing)

## Benchmark
### Long audio without speculative decoding:
```
Audio duration: 77.30 seconds
Transcription time: 8.15 s ± 49.4 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
Real-time factor (RTF): 0.11
```
### Short audio without speculative decoding:
```
Audio duration: 4.44 seconds
Transcription time: 1.04 s ± 60.3 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
Real-time factor (RTF): 0.23
```
### Short audio with speculative decoding:
```
Audio duration: 4.44 seconds
Transcription time: 670 ms ± 37.2 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
Real-time factor (RTF): 0.15
```

## Sample Input
```python
filepath = "sample.mp3"
with open(filepath, 'rb') as f:
    audio_encoded = base64.b64encode(f.read()).decode("utf-8")
content = Content(content_type="audio/mpeg", data=audio_encoded)
config = config_cls(batch_size=24)
```

## Sample Output
```python
result = extractor.extract(content, config)
text_content = next(content.data.decode('utf-8') for content in result)
print(text_content)
```
```
[{'speaker': 'SPEAKER_00', 'timestamp': (0.0, 1.0), 'text': ' Hi!'}, {'speaker': 'SPEAKER_00', 'timestamp': (1.0, 2.0), 'text': ' Hi.'}, {'speaker': 'SPEAKER_00', 'timestamp': (2.0, 3.0), 'text': ' You look amazing.'}, {'speaker': 'SPEAKER_01', 'timestamp': (3.0, 4.0), 'text': ' Thank you. You do too.'}, {'speaker': 'SPEAKER_00', 'timestamp': (4.0, 6.0), 'text': ' Oh my god, thanks. So who are we wearing tonight?'}, {'speaker': 'SPEAKER_01', 'timestamp': (6.0, 9.0), 'text': " I'm wearing Berluti. I went matte black everything."}, {'speaker': 'SPEAKER_00', 'timestamp': (9.0, 10.0), 'text': ' Yeah.'}, {'speaker': 'SPEAKER_01', 'timestamp': (10.0, 13.0), 'text': " Kept it simple. So I didn't have too much going on, but it feels pretty good."}, {'speaker': 'SPEAKER_00', 'timestamp': (13.0, 17.0), 'text': " It's super classic, but it's like chic. It's amazing."}, {'speaker': 'SPEAKER_01', 'timestamp': (17.0, 18.0), 'text': ' Thank you.'}, {'speaker': 'SPEAKER_00', 'timestamp': (18.0, 22.0), 'text': ' So are you into fashion? Or are you kind of new to the fashion world?'}, {'speaker': 'SPEAKER_01', 'timestamp': (22.0, 24.0), 'text': ' I would consider myself new to the fashion world.'}, {'speaker': 'SPEAKER_00', 'timestamp': (24.0, 27.38), 'text': ' I, you know, this is like Mark said, fish out of water a little bit.'}, {'speaker': 'SPEAKER_01', 'timestamp': (27.38, 29.72), 'text': " But I couldn't say no to the invitation."}, {'speaker': 'SPEAKER_00', 'timestamp': (29.72, 32.24), 'text': " I'm opening my eyes about the world of fashion right now."}, {'speaker': 'SPEAKER_00', 'timestamp': (32.24, 33.24), 'text': " It's very cool."}, {'speaker': 'SPEAKER_00', 'timestamp': (33.24, 37.6), 'text': " Well, I feel like for I started as a YouTuber also, and I didn't know anything about the"}, {'speaker': 'SPEAKER_00', 'timestamp': (37.6, 40.92), 'text': " world of fashion until I got invited to something I couldn't say no to."}, {'speaker': 'SPEAKER_00', 'timestamp': (40.92, 41.92), 'text': ' Changed my life forever.'}, {'speaker': 'SPEAKER_00', 'timestamp': (41.92, 42.92), 'text': " Now I'm like obsessed."}, {'speaker': 'SPEAKER_01', 'timestamp': (42.92, 43.92), 'text': ' Yeah.'}, {'speaker': 'SPEAKER_00', 'timestamp': (43.92, 44.92), 'text': ' I think the same thing might happen to you.'}, {'speaker': 'SPEAKER_01', 'timestamp': (44.92, 47.02), 'text': ' Might have to start reviewing some fashion stuff.'}, {'speaker': 'SPEAKER_01', 'timestamp': (47.02, 49.24), 'text': ' That would be a nice change of pace maybe.'}, {'speaker': 'SPEAKER_00', 'timestamp': (49.24, 52.42), 'text': ' So what are you most excited to see inside?'}, {'speaker': 'SPEAKER_01', 'timestamp': (52.42, 54.78), 'text': ' Man, my expectations are all over the place.'}, {'speaker': 'SPEAKER_01', 'timestamp': (54.78, 57.2), 'text': " I've heard that the performance might be great,"}, {'speaker': 'SPEAKER_00', 'timestamp': (57.2, 60.28), 'text': ' the food might be great, the people clearly are great.'}, {'speaker': 'SPEAKER_00', 'timestamp': (60.28, 62.48), 'text': ' So all around just looking for a good time.'}, {'speaker': 'SPEAKER_00', 'timestamp': (62.48, 63.66), 'text': " You're gonna have a great time in there."}, {'speaker': 'SPEAKER_00', 'timestamp': (63.66, 64.5), 'text': ' Go enjoy.'}, {'speaker': 'SPEAKER_01', 'timestamp': (64.5, 65.96), 'text': " I will. See you in there. This is just elegant a good time. You're going to have a great time in there. Go enjoy. I will. You in there. Yeah."}, {'speaker': 'SPEAKER_01', 'timestamp': (65.96, 68.3), 'text': ' This is just elegant.'}, {'speaker': 'SPEAKER_00', 'timestamp': (68.38, 69.5), 'text': ' Appreciate it. Nailed it.'}, {'speaker': 'SPEAKER_01', 'timestamp': (69.5, 70.76), 'text': ' Good to hear from you.'}, {'speaker': 'SPEAKER_00', 'timestamp': (70.76, 71.8), 'text': ' Thank you. Thank you.'}, {'speaker': 'SPEAKER_01', 'timestamp': (74.02, 76.1), 'text': ' Why do I keep going back to this?'}, {'speaker': 'SPEAKER_00', 'timestamp': (76.1, 77.26), 'text': " You guys, it's so bad."}]
```