# PDF Extractors

To begin utilizing these extractors install the indexify-extractor CLI.

```bash
pip install indexify-extractor-sdk
```

## Download and Run
```bash
indexify-extractor download <download-link>
indexify-extractor join-server
```

| Name                 | Download link                  | Extractor Module Name                    |
|----------------------|--------------------------------|------------------------------------------|
| layoutlm_document_qa | hub://pdf/layoutlm_document_qa | layoutlm_document_qa:LayoutLMDocumentQA  |
| ocrmypdf             | hub://pdf/ocrmypdf             | ocr_my_pdf:OCRMyPDFExtractor             |
| unstructuredio       | hub://pdf/unstructuredio       | unstructured_pdf:UnstructuredIOExtractor |
| pdf-extractor        | hub://pdf/pdf-extractor        | pdf_extractor:PDFExtractor               |
| markdown             | hub://pdf/markdown             | markdown_extractor:MarkdownExtractor     |
| easyocrpdf           | hub://pdf/easyocrpdf           | ocr_extractor:OCRExtractor     |
