# Simple Invoice Extractor

This extractor parses some invoice-related data from a PDF.
It uses the pre-trained [donut model from huggingface](https://huggingface.co/docs/transformers/model_doc/donut).

Content[PDF] -> Content[Empty] + Features[JSON metadata of invoice].

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

Try out the extractor. Write your favorite (foreign) quote.

```bash
cd text-lid
indexify extractor extract --file invoice.pdf
```

## Container

* The container is not published yet. *

```bash
docker run --rm --mount type=bind,source="$HOME/.cache/huggingface/hub",target=/indexify/.cache/huggingface/hub --mount type=bind,source="$(pwd)/data/",target=/indexify/data/ yenicelik/simple-invoice-parser extractor extract --file invoice.pdf
```
