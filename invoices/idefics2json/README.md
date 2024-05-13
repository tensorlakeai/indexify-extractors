# Idefics2 for Receipt parsing

The goal for the model in this extractor is to generate a JSON that contains key fields (like food items and their corresponding prices) from receipts. We fine-tuned Idefics2 on the CORD dataset, which contains (receipt image, ground truth JSON) pairs.

### Example:
##### input:
```
Content(content_type="image/jpeg", data=f.read())
```

##### output:
```
[Content(content_type='text/plain', data=b'[{'nm': '3002-Kyoto Choco Mochi', 'unitprice': '14.000', 'cnt': 'x2', 'price': '28.000'}, {'nm': '1001-Choco Bun', 'price': '22.000'}, {'nm': '6001-Plastic Bag Small', 'price': '0', 'unitprice': '22.000', 'cnt': 'x1', 'total': {'total_price': '50.000', 'cashprice': '50.000', 'menuqty_cnt': '4'}}]', labels={})]
```

##### code:
```python
!indexify-extractor download hub://invoices/idefics2json
!indexify-extractor join-server

from indexify import IndexifyClient
client = IndexifyClient()

client.add_extraction_policy(extractor='tensorlake/idefics2json', name="json-extraction")

import requests
req = requests.get("https://huggingface.co/spaces/tensorlake/indexify-extractors/resolve/main/sample.jpg")

with open('sample.jpg','wb') as f:
    f.write(req.content)

client.upload_file(path="sample.jpg")
```