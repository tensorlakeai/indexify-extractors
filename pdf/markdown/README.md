Markdown extractor converts PDF, EPUB, and MOBI to markdown.  It's 10x faster than nougat, more accurate on most documents, and has low hallucination risk.

- Support for a range of PDF documents (optimized for books and scientific papers)
- Removes headers/footers/other artifacts
- Converts most equations to latex
- Formats code blocks and tables
- Support for multiple languages (although most testing is done in English).  See `settings.py` for a language list, or to add your own.
- Works on GPU, CPU, or MPS

## How it works

Markdown extractor uses Marker which is a pipeline of deep learning models:

- Extract text, OCR if necessary (heuristics, tesseract)
- Detect page layout ([layout segmenter](https://huggingface.co/vikp/layout_segmenter), [column detector](https://huggingface.co/vikp/column_detector))
- Clean and format each block (heuristics, [texify](https://huggingface.co/vikp/texify))
- Combine blocks and postprocess complete text (heuristics, [pdf_postprocessor](https://huggingface.co/vikp/pdf_postprocessor_t5))