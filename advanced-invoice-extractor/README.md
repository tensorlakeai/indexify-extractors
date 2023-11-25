# Advanced Invoice Extractor

This extractor extracts markdown from PDF files using [Nougat](https://huggingface.co/docs/transformers/main/model_doc/nougat), and then uses an LLM to extract structured, invoice-related data.
The extracted data looks as follows:

```json
{
    "DocumentDescription": "Invoice",
    "FromName": "David Yenicelik",
    "FromAddress": "5359 Peter Pan Road, New York, NY 94538",
    "ToName": "Hans Peter",
    "ToAddress": "45352 Southstreet, Union City, PA 94587",
    "ToPhone": "(303) 541-3481",
    "AmountDue": 10000,
    "Currency": "USD",
    "DueDate": "June 13, 2021",
    "OrderNumber": "2021-0127",
    "VATAmount": null,
    "InputTax": null,
    "VATCode": null,
    "Quarter": null,
    "BookingDate": null,
    "DocumentDate": "June 13, 2021",
    "DocumentNumber": "2021-0127",
    "Remarks": "Progress Payment due as all the work is completed",
    "ConfidenceScore": 0.9
}
```

Content[Audio] -> Content[Empty] + Features[JSON metadata of transcription]

## Usage

Try out the extractor. Download your favorite invoice(!).

```
cd whisper-asr
indexify extractor extract --file twiml-ai-podcast.mp3
```

## Container

* The container is not published yet. *

<!-- docker run  -it diptanu/whisper-asr extract --file all-in-e154.mp3 -->

```
docker run --mount type=bind,source="$HOME/.cache/huggingface/",target=/indexify/.cache/huggingface/ --rm -e RUST_LOG=debug yenicelik/advanced-invoice-parser extractor extract --file data/homedepot/Invoice_KulwinderSingh_05172023.pdf
```
