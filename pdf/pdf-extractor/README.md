# Multipurpose PDF Extractor

This is a multipurpose PDF Extractor that can extract text, images and tables from PDF files. For text and image extraction we use PyPDF and for table extraction we use [Table Transformer](https://github.com/microsoft/table-transformer) from Microsoft.

This is able to extract all kinds of tables from PDFs, even the ones that have no boundaries which are undetected by other models.

### Example:
##### input:
```
Content(content_type="application/pdf", data=f.read())
```

##### output:
```
[Content(content_type='text/plain', data=b'I love playing football.', features=[Feature(feature_type='metadata', name='text', value={'page': 1}, comment=None)], labels={})]
```