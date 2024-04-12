from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel
from transformers import pipeline

class InputParams(BaseModel):
    max_length: int = 130
    min_length: int = 30

class SummaryExtractor(Extractor):
    name = "tensorlake/summarization"
    description = "A strong summarization extractor trained on English news articles. Excels at generating factual summaries."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super().__init__()
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def extract(self, content: Content, params: InputParams = None) -> List[Union[Feature, Content]]:
        contents = []

        max_length = getattr(params, 'max_length', 130)
        min_length = getattr(params, 'min_length', 30)

        article = content.data.decode("utf-8")
        summary = self.summarizer(article, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
        feature = Feature.metadata(value={"original_length": len(article), "summary_length": len(summary)}, name="text")
        contents.append(Content.from_text(summary, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return self.sample_text()

if __name__ == "__main__":
    article = """New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York. A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband. Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other. In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage. Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the 2010 marriage license application, according to court documents. Prosecutors said the marriages were part of an immigration scam. On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further. After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002. All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say. Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages. Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted. The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali. Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force. If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18."""
    text_data = Content(content_type="text/plain", data=article)
    input_params = InputParams(max_length=150, min_length=50)
    extractor = SummaryExtractor()
    results = extractor.extract(text_data, params=input_params)
    print(results)