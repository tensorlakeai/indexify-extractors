# OCRMyPDF
This extractor uses ocrmypdf to generate searchable PDF/A content from a regular PDF and then extract the text into plain text content.

Output Content:
text/plain for each page


### Input parameters

- **`deskew`**: `Optional[bool] = None`  
  Deskews crooked PDFs, helping in correcting the alignment of scanned documents.

- **`language`**: `Optional[Iterable[str]] = None`  
  Specifies the language(s) of the documents for improved OCR accuracy by using language-specific character recognition models.

- **`remove_background`**: `Optional[bool] = None`  
  Removes varied or distracting backgrounds from documents, enabling the OCR engine to focus more effectively on the text.

- **`rotate_pages`**: `Optional[bool] = None`  
  Automatically rotates pages to their correct orientation, which can significantly improve the readability and success rate of OCR processes.


### Additional Language Support
This extractor depends on having [tesseract](https://github.com/tesseract-ocr/tesseract) installed.

Install for Mac users
```bash
brew install tesseract
```

Install for Linux/Ubuntu
```bash
sudo apt install tesseract-ocr
```

To view currently installed language packs
```bash
tesseract --list-langs
```

To search for additional language packs:
```bash
apt search tesseract-ocr
```