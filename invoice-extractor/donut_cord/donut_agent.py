import os
import zipfile
import pandas as pd
from base_cord_v2 import DonutBaseV2, SimpleInvoiceParserInputParams

class InvoiceAgent:

    def __init__(self, invoice_directory):
        self.invoice_directory = invoice_directory
        self.extractor = DonutBaseV2()
        self.invoices_df = pd.DataFrame()

    def process_invoices(self):
        extracted_data = []

        for invoice_file in os.listdir(self.invoice_directory):
            if invoice_file.endswith(('.jpg', '.png', '.pdf')):
                file_path = os.path.join(self.invoice_directory, invoice_file)
                with open(file_path, 'rb') as file:
                    invoice_data = file.read()
                    extracted_info = self.extractor.extract(invoice_data, SimpleInvoiceParserInputParams())
                    standardized_info = self._standardize_data(extracted_info)
                    extracted_data.append(standardized_info)

        self.invoices_df = pd.DataFrame(extracted_data)

    def _standardize_data(self, extracted_data):
        standardized_data = {
            'invoice_id': extracted_data.get('invoice_id', ''),
            'total_value': extracted_data.get('total_value', 0),
            'date': extracted_data.get('date', ''),
        }
        return standardized_data

    def query_invoices(self, value_threshold):
        count = self.invoices_df[self.invoices_df['total_value'].astype(float) > value_threshold].shape[0]
        return count

    def save_to_csv(self, file_name):
        self.invoices_df.to_csv(file_name, index=False)

def unzip_invoices(zip_file_path, extract_to_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_folder)
    return extract_to_folder

def get_user_input():
    zip_file = input("Enter the path to the zip file containing invoices: ")
    query_value = float(input("Enter the total value to query invoices: "))
    return zip_file, query_value

if __name__ == "__main__":
    zip_file_path, query_value = get_user_input()

    # Unzip the invoices
    invoice_directory = 'invoices'
    unzip_invoices(zip_file_path, invoice_directory)

    # Process and query invoices
    agent = InvoiceAgent(invoice_directory)
    agent.process_invoices()
    agent.save_to_csv('extracted_invoices.csv')

    num_invoices = agent.query_invoices(query_value)
    print(f"Number of invoices with total value more than {query_value}: {num_invoices}")
