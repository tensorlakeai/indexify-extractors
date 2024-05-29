# NER

bert-base-NER is a fine-tuned BERT model that is ready to use for Named Entity Recognition and achieves state-of-the-art performance for the NER task. It has been trained to recognize four types of entities: location (LOC), organizations (ORG), person (PER) and Miscellaneous (MISC).

Specifically, this model is a bert-base-cased model that was fine-tuned on the English version of the standard CoNLL-2003 Named Entity Recognition dataset.

## Example

### Input
```python
sentence = Content.from_text("My name is Wolfgang and I live in Berlin")
input_params = NERExtractorConfig(model_name="dslim/bert-base-NER")
extractor = NERExtractor()
results = extractor.extract(sentence, params=input_params)
```

### Output
```
[Content(content_type='text/plain', data=b'B-PER: Wolfgang', features=[Feature(feature_type='metadata', name='metadata', value={'entity': 'B-PER', 'score': 0.9990139007568359, 'index': 4, 'word': 'Wolfgang', 'start': 11, 'end': 19}, comment=None)], labels={}), Content(content_type='text/plain', data=b'B-LOC: Berlin', features=[Feature(feature_type='metadata', name='metadata', value={'entity': 'B-LOC', 'score': 0.9996449947357178, 'index': 9, 'word': 'Berlin', 'start': 34, 'end': 40}, comment=None)], labels={})]
```