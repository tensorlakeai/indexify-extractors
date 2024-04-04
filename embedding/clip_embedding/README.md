# OpenAI Clip Embedding Extractor

This extractor implements OpenAI's CLIP (Contrastive Language–Image Pre-training) to extract embeddings from both images and text. 

When CLIP processes an image, it generates an image embedding; when it processes text, it generates a text embedding. These embeddings are created by separate components of the model (an image encoder and a text encoder) but are designed to be comparable.