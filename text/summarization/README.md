# BART based Summary Extractor

This is a BART based Summary Extractor that can convert text from Audio, PDF and other files to their summaries. For summary extraction we use [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) which is a strong summarization model trained on English news articles. Excels at generating factual summaries. For chunking we use FastRecursiveTextSplitter along with support for LangChain based text splitters.

### Example:
##### input:
```
Content(content_type="text/plain", data=article)
```

##### output:
```
[Content(content_type='text/plain', data=b' Liana Barrientos has been married 10 times, sometimes within two weeks of each other. Prosecutors say the marriages were part of an immigration scam. She is believed to still be married to four men, and at one time, she was married to eight men.', features=[Feature(feature_type='metadata', name='text', value={'original_length': 369, 'summary_length': 44, 'num_chunks': 1}, comment=None)], labels={})]
```