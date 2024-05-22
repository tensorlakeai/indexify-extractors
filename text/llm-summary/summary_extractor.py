from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel
from transformers import pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter, LatexTextSplitter
from .utils.chunk_module import FastRecursiveTextSplitter

class InputParams(BaseModel):
    max_length: int = 130
    chunk_method: str = "indexify" # recursive, markdown, latex

class SummaryExtractor(Extractor):
    name = "tensorlake/llm-summary"
    description = "A LLM based summarization extractor."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super().__init__()
        self.summarizer = pipeline("text-generation", model="h2oai/h2o-danube2-1.8b-chat", device_map="auto")

    def extract(self, content: Content, params: InputParams) -> List[Union[Feature, Content]]:
        contents = []
        full_summary = ""

        article = content.data.decode("utf-8")

        max_length = getattr(params, 'max_length', len(article)//4)
        chunk_method = getattr(params, 'chunk_method', 'indexify')

        if chunk_method == "recursive":
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=20)
            docs = text_splitter.create_documents([article])
            article_chunks = [doc.page_content for doc in docs]
        elif chunk_method == "markdown":
            text_splitter = MarkdownTextSplitter(chunk_size=512, chunk_overlap=20)
            docs = text_splitter.create_documents([article])
            article_chunks = [doc.page_content for doc in docs]
        elif chunk_method == "latex":
            text_splitter = LatexTextSplitter(chunk_size=512, chunk_overlap=20)
            docs = text_splitter.create_documents([article])
            article_chunks = [doc.page_content for doc in docs]
        else:
            text_splitter = FastRecursiveTextSplitter(512)
            docs = text_splitter.create_documents([article])
            article_chunks = [doc.page_content for doc in docs]
        
        num_chunks = len(article_chunks)

        for item in article_chunks:
            messages = [
                {"role": "user", "content": f"Summarize this in {max_length//num_chunks} words: {item}"}
            ]
            prompt = self.summarizer.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            res = self.summarizer(
                prompt,
                max_new_tokens=(max_length//num_chunks)*2,
                return_full_text=False
            )
            summary = res[0]["generated_text"]
            full_summary = " ".join([full_summary, summary])

        feature = Feature.metadata(value={"original_length": len(article.split()), "summary_length": len(full_summary.split()), "num_chunks": num_chunks}, name="text")
        contents.append(Content.from_text(full_summary, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    article = """New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York. A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband. Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other. In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage. Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the 2010 marriage license application, according to court documents. Prosecutors said the marriages were part of an immigration scam. On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further. After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002. All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say. Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages. Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted. The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali. Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force. If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18."""
    text_data = Content(content_type="text/plain", data=article)
    input_params = InputParams(max_length=150)
    extractor = SummaryExtractor()
    results = extractor.extract(text_data, params=input_params)
    print(results)