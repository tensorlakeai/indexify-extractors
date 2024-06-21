# Running the Benchmark Locally

## Start Indexify Server


```bash 
curl https://getindexify.ai | sh
./indexify server -d
```

## Download and Start Extractors

```bash
virtualenv ve
source ve/bin/activate
pip install indexify-extractor-sdk indexify
indexify-extractor download tensorlake/marker
indexify-extractor download tensorlake/easyocr
indexify-extractor download tensorlake/ocrmypdf
indexify-extractor download tensorlake/unstructuredio
```

```bash
indexify-extractor join-server
```

## Run the Benchamrk

To run the benchmark locally, execute the following commands before running `benchmark.py`:

```bash
source ve/bin/activate
sudo apt install libmagic-dev poppler-utils tesseract-ocr
pip install -q -r requirements.txt
wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
export TESSDATA_PREFIX=["PATH OF eng.traineddata"]

python benchmark.py
```
