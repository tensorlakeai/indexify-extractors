# Donut CORD V2

This extractor parses pdf or image form of invoice which is provided in JSON format. It uses the pre-trained [donut cord fine-tune model from huggingface](https://huggingface.co/naver-clova-ix/donut-base-finetuned-cord-v2).
This model is specially good at extracting list of product and its price from invoice.

Example input:

```text
<PDF or Image file of the invoice>
```

Example output:

```json
{
    "invoice_simple_donut_cord_v2": {
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
cd invoice-extractor/donut_cord
indexify extractor extract --file invoice.pdf
```

## Container

* The container is not published yet. *

```bash
docker run  -it indexify-extractors/donut_cord extractor extract --file invoice.pdf
```