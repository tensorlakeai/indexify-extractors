from typing import List, Union
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel
from transformers import pipeline
from openai import OpenAI

class InputParams(BaseModel):
    llm: str = "openai"
    key: str = None
    prompt: str = "You are a helpful assistant."
    query: str = None

class GenAIExtractor(Extractor):
    name = "tensorlake/genai"
    description = "An extractor that let's you use multiple LLMs."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super().__init__()

    def extract(self, content: Content, params = InputParams) -> List[Union[Feature, Content]]:
        contents = []
        text = content.data.decode("utf-8")

        llm = getattr(params, 'llm')
        key = getattr(params, 'key')
        prompt = getattr(params, 'prompt')
        query = getattr(params, 'query')
        if query is None:
            query = text

        if llm == "openai":
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ]
            )
            response_content = response.choices[0].message.content
            feature = Feature.metadata(value={"model": response.model, "completion_tokens": response.usage.completion_tokens, "prompt_tokens": response.usage.prompt_tokens}, name="text")
        
        contents.append(Content.from_text(response_content, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract information according to this schema and return json in this format {"Invoice No.": "", "Date": "", "Account Number": "", "Owner": "", "Property": "", "Address": "", "Registration Key": "", "Last Month Balance": "", "Current Amount Due": "", "Due Date": ""}:
    Axis\nSTATEMENTInvoice No. "Invoice No."\nDate: 4/19/2024\nAccount Number:\nOwner:\nProperty:"Account Number"\n"Owner"\n"Property"\n"Owner"\n"Property"\n"Address"SUMMARY OF ACCOUNT\nLast Month Balance:\nCurrent Amount Due:"Last Month Balance"\n"Current Amount Due"\nAccount details on back.\nProfessionally\nprepared by:\nSTATEMENT MESSAGE\nWelcome to Action Property Management! We are excited to be\nserving your community. Our Community Care team is more than\nhappy to assist you with any billing questions you may have. For\ncontact options, please visit www.actionlife.com/contact. Visit the\nAction Property Management web page at: www.actionlife.com.BILLING QUESTIONS\nScan the QR code to\ncontact our\nCommunity Care\nteam.\nactionlife.com/contact\nCommunityCare@actionlife.com\nRegister your Resident\nPortal account now!\nRegistration Key/ID:\n"Registration Key"\nresident.actionlife.com\nTo learn more about issues facing HOAs, say "Hey Siri, search the web for The Uncommon Area by Action Property Management."\nMake checks payable to:\nAxisAccount Number: "Account Number"\nOwner: "Owner"\nPLEASE REMIT PAYMENT TO:\n** AUTOPAY SCHEDULED **\n** NO REMITTANCE NECESSARY **CURRENT AMOUNT DUE\n"Current Amount Due"\nDUE DATE\n"Due Date"\n0049 00008330 0000922000203826 7 00065303 00000000 9"""
    article = Content.from_text('Axis\nSTATEMENTInvoice No. 20240501-336593\nDate: 4/19/2024\nAccount Number:\nOwner:\nProperty:922000203826\nJohn Doe\n200 Park Avenue, Manhattan\nJohn Doe\n200 Park Avenue Manhattan\nNew York 10166SUMMARY OF ACCOUNT\nLast Month Balance:\nCurrent Amount Due:$653.03\n$653.03\nAccount details on back.\nProfessionally\nprepared by:\nSTATEMENT MESSAGE\nWelcome to Action Property Management! We are excited to be\nserving your community. Our Community Care team is more than\nhappy to assist you with any billing questions you may have. For\ncontact options, please visit www.actionlife.com/contact. Visit the\nAction Property Management web page at: www.actionlife.com.BILLING QUESTIONS\nScan the QR code to\ncontact our\nCommunity Care\nteam.\nactionlife.com/contact\nCommunityCare@actionlife.com\nRegister your Resident\nPortal account now!\nRegistration Key/ID:\nFLOWR2U\nresident.actionlife.com\nTo learn more about issues facing HOAs, say "Hey Siri, search the web for The Uncommon Area by Action Property Management."\nMake checks payable to:\nAxisAccount Number: 922000203826\nOwner: John Doe\nPLEASE REMIT PAYMENT TO:\n** AUTOPAY SCHEDULED **\n** NO REMITTANCE NECESSARY **CURRENT AMOUNT DUE\n$653.03\nDUE DATE\n5/1/2024\n0049 00008330 0000922000203826 7 00065303 00000000 9')
    input_params = InputParams(llm="openai", key="", prompt=prompt)
    extractor = GenAIExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)