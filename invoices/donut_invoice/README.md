# Simple Invoice Extractor

This extractor parses some invoice-related data from a PDF.
It uses the pre-trained [donut model from huggingface](https://huggingface.co/docs/transformers/model_doc/donut).

Content[String] -> Content[Empty] + Features[JSON metadata of invoice].

Example input:

```text
<PDF file of an Invoice>
```

Example output:

```json
{
    "invoice_simple_donut": {
        "DocType": "Invoice",
        "Currency1": "CHF",
        "DocumentDate": "2023-01-11",
        "GrossAmount": "269.25",
        "InvoiceNumber": "8037",
        "NetAmount1": "250.00",
        "TaxAmount1": "19.25"
    }
}
```

## Usage

Try out the extractor. Use any invoice you have.

```bash
cd invoice-extractor/donut_invoice
indexify extractor extract --file invoice.pdf
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/donut_invoice extractor extract --file invoice.pdf
```
