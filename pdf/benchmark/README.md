### Running the Benchmark Locally

To run the benchmark locally, execute the following commands before running `benchmark.py`:

```bash
sudo apt install libmagic-dev poppler-utils tesseract-ocr
pip install -q -r requirements.txt
wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
export TESSDATA_PREFIX=["PATH OF eng.traineddata"]
```