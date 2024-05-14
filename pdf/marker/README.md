# PDF to Markdown Extraction

Markdown extractor converts PDF, EPUB, and MOBI to markdown.  It's 10x faster than nougat, more accurate on most documents, and has low hallucination risk.

- Support for a range of PDF documents (optimized for books and scientific papers)
- Removes headers/footers/other artifacts
- Converts most equations to latex
- Formats code blocks and tables
- Support for multiple languages (although most testing is done in English).  See `settings.py` for a language list, or to add your own.
- Works on GPU, CPU, or MPS

## Requirements
`pip install marker-pdf`

## How it works

Markdown extractor uses Marker which is a pipeline of deep learning models:

- Extract text, OCR if necessary (heuristics, tesseract)
- Detect page layout ([layout segmenter](https://huggingface.co/vikp/layout_segmenter), [column detector](https://huggingface.co/vikp/column_detector))
- Clean and format each block (heuristics, [texify](https://huggingface.co/vikp/texify))
- Combine blocks and postprocess complete text (heuristics, [pdf_postprocessor](https://huggingface.co/vikp/pdf_postprocessor_t5))

### Example:
##### input:
```
Content(content_type="application/pdf", data=f.read())
```

##### output:
```
[Content(content_type='text/plain', data=b'', features=[Feature(feature_type='metadata', name='text', value={'language': 'English', 'filetype': 'pdf', 'toc': [], 'pages': 1, 'ocr_stats': {'ocr_pages': 0, 'ocr_failed': 0, 'ocr_success': 0}, 'block_stats': {'header_footer': 2, 'code': 0, 'table': 0, 'equations': {'successful_ocr': 0, 'unsuccessful_ocr': 0, 'equations': 0}}, 'postprocess_stats': {'edit': {}}}, comment=None)], labels={})]
```

##### code:
```python
!indexify-extractor download hub://pdf/markdown
!indexify-extractor join-server markdown.markdown_extractor:MarkdownExtractor

from indexify import IndexifyClient
client = IndexifyClient()

client.add_extraction_policy(extractor='tensorlake/markdown-extractor', name="markdown-extraction")

import requests
req = requests.get("https://arxiv.org/pdf/2310.16944.pdf")

with open('2310.16944.pdf','wb') as f:
    f.write(req.content)

client.upload_file(path="2310.16944.pdf")
```