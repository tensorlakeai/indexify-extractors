# LayoutLM Document QA

LayoutLM is a pre-trained model introduced by researchers at Microsoft for document image understanding tasks, which combines visual, textual, and layout information to better understand documents. It's particularly designed to handle the challenge of understanding documents where the layout plays a crucial role in the overall understanding of the content, such as invoices, forms, and scientific papers.

This extractor uses the pretrained model from huggingface https://huggingface.co/impira/layoutlm-document-qa

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