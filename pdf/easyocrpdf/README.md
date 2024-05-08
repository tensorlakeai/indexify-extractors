# EasyOCR
This extractor uses EasyOCR to generate searchable PDF/A content from a regular PDF and then extract the text into plain text content.

Output:
text/plain for each page

### Example
##### content (pdf):
<img src="image-based.png" style="max-width:400px;" alt="PDF" title="PDF">

##### Output
```json
[
  {
    "contentType": "text/plain",
    "data": "This is an example of an “Image-based PDF” (also known as image-only PDFs).\nImage-based PDFs are typically created through scanning paper in a copier, taking photographs\nor taking screenshots. To a computer, they are images. Though we humans can see text in the\nimage, the file only consists of the image layer but not the searchable text layer that True PDFs\ncontain. As a result, we cannot use a computer to search the text we see in the image as that text\nlayer is missing. There are times when discovery is produced, it will be in an image-based PDF\nformat. When you come across image-based PDFs, ask the U.S. Attorney’s Office in what\nformat was that file originally. Second, ask if they have it in a searchable format and specifically\nif they have it in a digitally created, True, Text-based PDF format. They may not, as they often\nreceive PDFs from other sources before they provide them to you, but you will want to know\nwhat is the format in which they have it in, and what is the original format of the file (as far as\nthey know).\n",
    "features": [
      {
        "featureType": "metadata",
        "name": "metadata",
        "value": {
          "page": 0
        }
      }
    ]
  }
]
```