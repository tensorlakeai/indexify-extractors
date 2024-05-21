from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
from transformers import pipeline
import os
from openai import OpenAI
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class LLMExtractorConfig(BaseModel):
    service: str = Field(default='openai')
    model_name: Optional[str] = Field(default='gpt-3.5-turbo')
    key: Optional[str] = Field(default=None)
    prompt: str = Field(default='You are a helpful assistant.')
    query: Optional[str] = Field(default=None)

class LLMExtractor(Extractor):
    name = "tensorlake/llm"
    description = "An extractor that let's you use multiple LLMs."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super(LLMExtractor, self).__init__()

    def extract(self, content: Content, params: LLMExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        text = content.data.decode("utf-8")

        service = params.service
        model_name = params.model_name
        key = params.key
        prompt = params.prompt
        query = params.query
        if query is None:
            query = text

        if service == "openai":
            if ('OPENAI_API_KEY' not in os.environ) and (key is None):
                response_content = "The OPENAI_API_KEY environment variable is not present."
                feature = Feature.metadata(value={"model": model_name}, name="text")
            else:
                if ('OPENAI_API_KEY' in os.environ) and (key is None):
                    client = OpenAI()
                else:
                    client = OpenAI(api_key=key)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query}
                    ]
                )
                response_content = response.choices[0].message.content
                feature = Feature.metadata(value={"model": response.model, "completion_tokens": response.usage.completion_tokens, "prompt_tokens": response.usage.prompt_tokens}, name="text")
        
        if service == "gemini":
            if ('GEMINI_API_KEY' not in os.environ) and (key is None):
                response_content = "The GEMINI_API_KEY environment variable is not present."
                feature = Feature.metadata(value={"model": model_name}, name="text")
            else:
                if ('GEMINI_API_KEY' in os.environ) and (key is None):
                    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                else:
                    genai.configure(api_key=key)
                generation_config = { "temperature": 1, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192, "response_mime_type": "text/plain", }
                safety_settings = [ { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE", }, { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE", }, { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE", }, { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE", }, ]
                model = genai.GenerativeModel( model_name="gemini-1.5-flash-latest", safety_settings=safety_settings, generation_config=generation_config, )
                chat_session = model.start_chat( history=[ ] )
                response = chat_session.send_message(prompt + " " + query)
                response_content = response.text
                feature = Feature.metadata(value={"model": model_name}, name="text")
        
        if '/' in service:
            model = AutoModelForCausalLM.from_pretrained(service, device_map="cuda", torch_dtype="auto", trust_remote_code=True)
            tokenizer = AutoTokenizer.from_pretrained(service)
            messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            generation_args = {"max_new_tokens": 500, "return_full_text": False, "temperature": 0.0, "do_sample": False}
            output = pipe(messages, **generation_args)
            response_content = output[0]['generated_text']
            feature = Feature.metadata(value={"model": service}, name="text")
        
        contents.append(Content.from_text(response_content, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello world, I am a good boy.")

if __name__ == "__main__":
    prompt = """Extract information according to this schema and return json in this format {"Invoice No.": "", "Date": "", "Account Number": "", "Owner": "", "Property": "", "Address": "", "Registration Key": "", "Last Month Balance": "", "Current Amount Due": "", "Due Date": ""}:
    Axis\nSTATEMENTInvoice No. "Invoice No."\nDate: 4/19/2024\nAccount Number:\nOwner:\nProperty:"Account Number"\n"Owner"\n"Property"\n"Owner"\n"Property"\n"Address"SUMMARY OF ACCOUNT\nLast Month Balance:\nCurrent Amount Due:"Last Month Balance"\n"Current Amount Due"\nAccount details on back.\nProfessionally\nprepared by:\nSTATEMENT MESSAGE\nWelcome to Action Property Management! We are excited to be\nserving your community. Our Community Care team is more than\nhappy to assist you with any billing questions you may have. For\ncontact options, please visit www.actionlife.com/contact. Visit the\nAction Property Management web page at: www.actionlife.com.BILLING QUESTIONS\nScan the QR code to\ncontact our\nCommunity Care\nteam.\nactionlife.com/contact\nCommunityCare@actionlife.com\nRegister your Resident\nPortal account now!\nRegistration Key/ID:\n"Registration Key"\nresident.actionlife.com\nTo learn more about issues facing HOAs, say "Hey Siri, search the web for The Uncommon Area by Action Property Management."\nMake checks payable to:\nAxisAccount Number: "Account Number"\nOwner: "Owner"\nPLEASE REMIT PAYMENT TO:\n** AUTOPAY SCHEDULED **\n** NO REMITTANCE NECESSARY **CURRENT AMOUNT DUE\n"Current Amount Due"\nDUE DATE\n"Due Date"\n0049 00008330 0000922000203826 7 00065303 00000000 9"""
    article = Content.from_text('Axis\nSTATEMENTInvoice No. 20240501-336593\nDate: 4/19/2024\nAccount Number:\nOwner:\nProperty:922000203826\nJohn Doe\n200 Park Avenue, Manhattan\nJohn Doe\n200 Park Avenue Manhattan\nNew York 10166SUMMARY OF ACCOUNT\nLast Month Balance:\nCurrent Amount Due:$653.03\n$653.03\nAccount details on back.\nProfessionally\nprepared by:\nSTATEMENT MESSAGE\nWelcome to Action Property Management! We are excited to be\nserving your community. Our Community Care team is more than\nhappy to assist you with any billing questions you may have. For\ncontact options, please visit www.actionlife.com/contact. Visit the\nAction Property Management web page at: www.actionlife.com.BILLING QUESTIONS\nScan the QR code to\ncontact our\nCommunity Care\nteam.\nactionlife.com/contact\nCommunityCare@actionlife.com\nRegister your Resident\nPortal account now!\nRegistration Key/ID:\nFLOWR2U\nresident.actionlife.com\nTo learn more about issues facing HOAs, say "Hey Siri, search the web for The Uncommon Area by Action Property Management."\nMake checks payable to:\nAxisAccount Number: 922000203826\nOwner: John Doe\nPLEASE REMIT PAYMENT TO:\n** AUTOPAY SCHEDULED **\n** NO REMITTANCE NECESSARY **CURRENT AMOUNT DUE\n$653.03\nDUE DATE\n5/1/2024\n0049 00008330 0000922000203826 7 00065303 00000000 9')
    input_params = LLMExtractorConfig(service="openai", prompt=prompt)
    extractor = LLMExtractor()
    results = extractor.extract(article, params=input_params)
    print(results)