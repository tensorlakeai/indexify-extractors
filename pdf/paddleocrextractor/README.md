# PaddleOCR PDF Extractor

This is a PaddleOCR based PDF extractor formulated using the [PaddleOCR] (https://github.com/PaddlePaddle/PaddleOCR/tree/release/2.7) library. 
The PaddleOCR PDF Extractor API leverages the capabilities of PaddlePaddle OCR to efficiently extract text from various types of PDF documents. It supports multiple languages and can handle diverse document formats, including invoices, academic papers, and forms. PaddleOCR integrates many OCR algorithms, text detection algorithms include DB, EAST, SAST, etc., text recognition algorithms include CRNN, RARE, StarNet, Rosetta, SRN and other algorithms.

### Example:
##### input:
```
Content(content_type="application/pdf", data=f.read())
```

##### output:
```
Content(content_type='text/plain', data=b"Form 1040\nForms W-2 & W-2G Summary\n2023\nKeep for your records\n Name(s) Shown on Return\nSocial Security Number\nJohn H & Jane K Doe\n321-12-3456\nEmployer\nTotal local tax withheld .", features=[Feature(feature_type='metadata', name='metadata', value={'type': 'text'}, comment=None)], labels={})]
```

##### python sdk:
```python
!indexify-extractor download hub://pdf/pdfextractor
!indexify-extractor join-server

from indexify import IndexifyClient
client = IndexifyClient()

client.add_extraction_policy(extractor='tensorlake/paddleocr_extractor', name="pdf-extraction")

import requests
req = requests.get("sample_form.pdf")

with open('sample_form.pdf','wb') as f:
    f.write(req.content)

client.upload_file(path="sample_form.pdf")
```

The extractor can also be chained with other extractors for maximum effect. 