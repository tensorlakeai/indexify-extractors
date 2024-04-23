# LLM based Summary Extractor

This is a LLM based Summary Extractor that can convert text from Audio, PDF and other files to their summaries. For summary extraction we use [h2oai/h2o-danube2-1.8b-chat](https://huggingface.co/h2oai/h2o-danube2-1.8b-chat) which is a strong <3B parameter Large Language Model suitable even for low end machines. For chunking we use FastRecursiveTextSplitter along with support for LangChain based text splitters.

### Example:
##### input:
```
Content(content_type="text/plain", data=article)
```

##### output:
```
[Content(content_type='text/plain', data=b' Liana Barrientos has been married 10 times, sometimes within two weeks of each other. Prosecutors say the marriages were part of an immigration scam. She is believed to still be married to four men, and at one time, she was married to eight men.', features=[Feature(feature_type='metadata', name='text', value={'original_length': 369, 'summary_length': 44, 'num_chunks': 1}, comment=None)], labels={})]
```