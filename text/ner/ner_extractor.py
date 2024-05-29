from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

class NERExtractorConfig(BaseModel):
    model_name: Optional[str] = Field(default="dslim/bert-base-NER")

class NERExtractor(Extractor):
    name = "tensorlake/ner"
    description = "An extractor that let's you do Named Entity Recognition."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super(NERExtractor, self).__init__()

    def extract(self, content: Content, params: NERExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        text = content.data.decode("utf-8")
        model_name = params.model_name

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        nlp = pipeline("ner", model=model, tokenizer=tokenizer)

        ner_results = nlp(text)
        for result in ner_results:
            result['score'] = float(result['score'])
            feature = Feature.metadata(value=result)
            contents.append(Content.from_text(f"{result['entity']}: {result['word']}", features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("My name is Wolfgang and I live in Berlin")

if __name__ == "__main__":
    sentence = Content.from_text("My name is Wolfgang and I live in Berlin")
    input_params = NERExtractorConfig(model_name="dslim/bert-base-NER")
    extractor = NERExtractor()
    results = extractor.extract(sentence, params=input_params)
    print(results)