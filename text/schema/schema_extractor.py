from typing import List, Union, Optional
from indexify_extractor_sdk import Content, Extractor, Feature
from pydantic import BaseModel, Field
from transformers import pipeline
import os
from typing import Dict, Optional
from openai import OpenAI
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class SchemaExtractorConfig(BaseModel):
    service: str = Field(default='openai')
    model_name: Optional[str] = Field(default='gpt-3.5-turbo')
    key: Optional[str] = Field(default=None)
    schema_config: Dict = Field(default={
        'properties': {'name': {'title': 'Name', 'type': 'string'}},
        'required': ['name'],
        'title': 'User',
        'type': 'object'
    }, alias='schema')
    data: Optional[str] = Field(default=None)
    additional_messages: str = Field(default='Extract information in JSON according to this schema and return only the output.')

    class Config:
        allow_population_by_field_name = True

class SchemaExtractor(Extractor):
    name = "tensorlake/schema"
    description = "An extractor that let's you extract JSON from schemas."
    system_dependencies = []
    input_mime_types = ["text/plain"]

    def __init__(self):
        super(SchemaExtractor, self).__init__()

    def extract(self, content: Content, params: SchemaExtractorConfig) -> List[Union[Feature, Content]]:
        contents = []
        text = content.data.decode("utf-8")

        service = params.service
        model_name = params.model_name
        key = params.key
        schema = params.schema
        example_text = params.example_text
        data = params.data
        additional_messages = params.additional_messages
        if data is None:
            data = text

        if service == "openai":
            if ('OPENAI_API_KEY' not in os.environ) and (key is None):
                response_content = "The OPENAI_API_KEY environment variable is not present."
                feature = Feature.metadata(value={"model": model_name}, name="text")
            else:
                if ('OPENAI_API_KEY' in os.environ) and (key is None):
                    client = OpenAI()
                else:
                    client = OpenAI(api_key=key)
                if schema is None and example_text:
                    schema = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "Extract a JSON schema based on the examples" + str(example_text)},
                            {"role": "user", "content": data}
                        ]
                    )
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": additional_messages + str(schema)},
                        {"role": "user", "content": data}
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
                if schema is None and example_text:
                    schema = chat_session.send_message("Extract a JSON schema based on the examples" + str(example_text))
                response = chat_session.send_message(additional_messages + str(schema) + " " + data)
                response_content = response.text
                feature = Feature.metadata(value={"model": model_name}, name="text")
        
        if '/' in service:
            model = AutoModelForCausalLM.from_pretrained(service, device_map="cuda", torch_dtype="auto", trust_remote_code=True)
            tokenizer = AutoTokenizer.from_pretrained(service)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            generation_args = {"max_new_tokens": 500, "return_full_text": False, "temperature": 0.0, "do_sample": False}
            if schema is None and example_text:
                schema_messages = [{"role": "system", "content": "Extract a JSON schema based on the examples" + str(example_text)}, {"role": "user", "content": data}]
                schema = pipe(schema_messages, **generation_args)
                schema = schema[0]['generated_text']
            messages = [{"role": "system", "content": additional_messages + str(schema)}, {"role": "user", "content": data}]
            output = pipe(messages, **generation_args)
            response_content = output[0]['generated_text']
            feature = Feature.metadata(value={"model": service}, name="text")
        
        contents.append(Content.from_text(response_content, features=[feature]))
        
        return contents

    def sample_input(self) -> Content:
        return Content.from_text("Hello, I am Diptanu from Tensorlake.")

if __name__ == "__main__":
    schema = {'properties': {'invoice_number': {'title': 'Invoice Number', 'type': 'string'}, 'date': {'title': 'Date', 'type': 'string'}, 'account_number': {'title': 'Account Number', 'type': 'string'}, 'owner': {'title': 'Owner', 'type': 'string'}, 'address': {'title': 'Address', 'type': 'string'}, 'last_month_balance': {'title': 'Last Month Balance', 'type': 'string'}, 'current_amount_due': {'title': 'Current Amount Due', 'type': 'string'}, 'registration_key': {'title': 'Registration Key', 'type': 'string'}, 'due_date': {'title': 'Due Date', 'type': 'string'}}, 'required': ['invoice_number', 'date', 'account_number', 'owner', 'address', 'last_month_balance', 'current_amount_due', 'registration_key', 'due_date'], 'title': 'User', 'type': 'object'}
    examples = [
    {
        "type": "object",
        "properties": {
            "employer_name": {"type": "string", "title": "Employer Name"},
            "employee_name": {"type": "string", "title": "Employee Name"},
            "wages": {"type": "number", "title": "Wages"},
            "federal_tax_withheld": {"type": "number", "title": "Federal Tax Withheld"},
            "state_wages": {"type": "number", "title": "State Wages"},
            "state_tax": {"type": "number", "title": "State Tax"}
        },
        "required": ["employer_name", "employee_name", "wages", "federal_tax_withheld", "state_wages", "state_tax"]
    },
    {
        "type": "object",
        "properties": {
            "booking_reference": {"type": "string", "title": "Booking Reference"},
            "passenger_name": {"type": "string", "title": "Passenger Name"},
            "flight_number": {"type": "string", "title": "Flight Number"},
            "departure_airport": {"type": "string", "title": "Departure Airport"},
            "arrival_airport": {"type": "string", "title": "Arrival Airport"},
            "departure_time": {"type": "string", "title": "Departure Time"},
            "arrival_time": {"type": "string", "title": "Arrival Time"}
        },
        "required": ["booking_reference", "passenger_name", "flight_number", "departure_airport", "arrival_airport", "departure_time", "arrival_time"]
    }]


    data = Content.from_text("Form 1040\nForms W-2 & W-2G Summary\n2023\nKeep for your records\n Name(s) Shown on Return\nSocial Security Number\nJohn H & Jane K Doe\n321-12-3456\nEmployer\nSP\nFederal Tax\nState Wages\nState Tax\nForm W-2\nWages\nAcmeware Employer\n143,433.\n143,433.\n1,000.\nTotals.\n143,433.\n143,433.\n1,000.\nForm W-2 Summary\nBox No.\nDescription\nTaxpayer\nSpouse\nTotal\nTotal wages, tips and compensation:\n1\na\nW2 box 1 statutory wages reported on Sch C\nW2 box 1 inmate or halfway house wages .\n6\nc\nAll other W2 box 1 wages\n143,433.\n143,433.\nd\nForeign wages included in total wages\ne\n0.\n0.\n2\nTotal federal tax withheld\n 3 & 7 Total social security wages/tips .\n143,566.\n143,566.\n4\nTotal social security tax withheld\n8,901.\n8,901.\n5\nTotal Medicare wages and tips\n143,566.\n143,566.\n6\nTotal Medicare tax withheld . :\n2,082.\n2,082.\n8\nTotal allocated tips .\n9\nNot used\n10 a\nTotal dependent care benefits\nb\nOffsite dependent care benefits\nc\nOnsite dependent care benefits\n11\n Total distributions from nonqualified plans\n12 a\nTotal from Box 12\n3,732.\n3,732.\nElective deferrals to qualified plans\n133.\n133.\nc\nRoth contrib. to 401(k), 403(b), 457(b) plans .\n.\n1 Elective deferrals to government 457 plans\n2 Non-elective deferrals to gov't 457 plans .\ne\nDeferrals to non-government 457 plans\nf\nDeferrals 409A nonqual deferred comp plan .\n6\nIncome 409A nonqual deferred comp plan .\nh\nUncollected Medicare tax :\nUncollected social security and RRTA tier 1\nj\nUncollected RRTA tier 2 . . .\nk\nIncome from nonstatutory stock options\nNon-taxable combat pay\nm\nQSEHRA benefits\nTotal other items from box 12 .\nn\n3,599.\n3,599.\n14 a\n Total deductible mandatory state tax .\nb\nTotal deductible charitable contributions\nc\nTotal state deductible employee expenses .\nd\n Total RR Compensation .\ne\nTotal RR Tier 1 tax .\nf\nTotal RR Tier 2 tax . -\nTotal RR Medicare tax .\ng\nh\nTotal RR Additional Medicare tax .\ni\nTotal RRTA tips. : :\nj\nTotal other items from box 14\nk\nTotal sick leave subject to $511 limit\nTotal sick leave subject to $200 limit\nm\nTotal emergency family leave wages\n16\nTotal state wages and tips .\n143,433.\n143,433.\n17\nTotal state tax withheld\n1,000.\n1,000.\n19\nTotal local tax withheld .")
    input_params = SchemaExtractorConfig(service="openai", schema=schema, example_text=str(examples))
    extractor = SchemaExtractor()
    results = extractor.extract(data, params=input_params)
    print(results)