# LLM Extractor

This is a LLM based Extractor that supports multiple LLMs. By default it uses OpenAI and works on the Content of previous extractor as data for schema extraction, however we can manually overwrite schema and data.

### Example:
##### input:
```
schema = {'properties': {'invoice_number': {'title': 'Invoice Number', 'type': 'string'}, 'date': {'title': 'Date', 'type': 'string'}, 'account_number': {'title': 'Account Number', 'type': 'string'}, 'owner': {'title': 'Owner', 'type': 'string'}, 'address': {'title': 'Address', 'type': 'string'}, 'last_month_balance': {'title': 'Last Month Balance', 'type': 'string'}, 'current_amount_due': {'title': 'Current Amount Due', 'type': 'string'}, 'registration_key': {'title': 'Registration Key', 'type': 'string'}, 'due_date': {'title': 'Due Date', 'type': 'string'}}, 'required': ['invoice_number', 'date', 'account_number', 'owner', 'address', 'last_month_balance', 'current_amount_due', 'registration_key', 'due_date'], 'title': 'User', 'type': 'object'}

data = Content.from_text('Axis\nSTATEMENTInvoice No. 20240501-336593\nDate: 4/19/2024\nAccount Number:\nOwner:\nProperty:922000203826\nJohn Doe\n200 Park Avenue, Manhattan\nJohn Doe\n200 Park Avenue Manhattan\nNew York 10166SUMMARY OF ACCOUNT\nLast Month Balance:\nCurrent Amount Due:$653.03\n$653.03\nAccount details on back.\nProfessionally\nprepared by:\nSTATEMENT MESSAGE\nWelcome to Action Property Management! We are excited to be\nserving your community. Our Community Care team is more than\nhappy to assist you with any billing questions you may have. For\ncontact options, please visit www.actionlife.com/contact. Visit the\nAction Property Management web page at: www.actionlife.com.BILLING QUESTIONS\nScan the QR code to\ncontact our\nCommunity Care\nteam.\nactionlife.com/contact\nCommunityCare@actionlife.com\nRegister your Resident\nPortal account now!\nRegistration Key/ID:\nFLOWR2U\nresident.actionlife.com\nTo learn more about issues facing HOAs, say "Hey Siri, search the web for The Uncommon Area by Action Property Management."\nMake checks payable to:\nAxisAccount Number: 922000203826\nOwner: John Doe\nPLEASE REMIT PAYMENT TO:\n** AUTOPAY SCHEDULED **\n** NO REMITTANCE NECESSARY **CURRENT AMOUNT DUE\n$653.03\nDUE DATE\n5/1/2024\n0049 00008330 0000922000203826 7 00065303 00000000 9')

input_params = SchemaExtractorConfig(service="openai", schema=schema)

extractor = SchemaExtractor()
results = extractor.extract(data, params=input_params)
```

##### output:
```
[Content(content_type='text/plain', data=b'{\n    "Invoice No.": "20240501-336593",\n    "Date": "4/19/2024",\n    "Account Number": "922000203826",\n    "Owner": "John Doe",\n    "Property": "200 Park Avenue, Manhattan",\n    "Address": "200 Park Avenue Manhattan, New York 10166",\n    "Registration Key": "FLOWR2U",\n    "Last Month Balance": "$653.03",\n    "Current Amount Due": "$653.03",\n    "Due Date": "5/1/2024"\n}', features=[Feature(feature_type='metadata', name='text', value={'model': 'gpt-3.5-turbo-0125', 'completion_tokens': 99, 'prompt_tokens': 564}, comment=None)], labels={})]
```