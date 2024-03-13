# LayoutLM Document QA

This is a fine-tuned version of the multi-modal [LayoutLM](https://aka.ms/layoutlm) model for the task of question answering on documents. It has been fine-tuned using both the SQuAD2.0 and [DocVQA](https://www.docvqa.org/) datasets.

This model combines visual, textual, and layout information to better understand documents. It's particularly designed to handle the challenge of understanding documents where the layout plays a crucial role in the overall understanding of the content, such as invoices, forms, and scientific papers.

This extractor uses the pretrained [model from huggingface](https://huggingface.co/impira/layoutlm-document-qa)

Input Parameters
- query: string - the query you want to perform on content

Example:
query: what is the invoice total?

the following metadata will be added to the content:
{
  "query": "what is the invoice total?",
  "answer": "$85.73",
  "page": 0,
  "score": 99.3692321,
}