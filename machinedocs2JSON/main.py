import os
from pdf_extractor import PDFTableExtractor
from data_processor import DataFrameProcessor
from extract_file_info import FileInformationExtractor
from json_formatter import JSONGenerator
import pandas as pd

pd.set_option('display.max_rows', 100)
filepath = "C:\\Users\\achabris\\desktop\\26553-HXM02-EXCAVATOR-1.24.05.2701 1.pdf"

information = FileInformationExtractor(file_path=filepath)
number_of_d2_pages = information.get_number_of_d2_pages()

# Use this number to dynamically set the pages to extract
pages_to_extract = ','.join(str(i) for i in range(2, 2 + number_of_d2_pages))

extractor = PDFTableExtractor(file_path=filepath, pages_to_extract_from=pages_to_extract)
tables = extractor.extract_tables()

# Process all extracted tables
processed_dfs = DataFrameProcessor.process_multiple([table.df for table in tables])

# Extract file information
information = FileInformationExtractor(file_path=filepath)
information.extract_text_to_dataframes()
file_details_df = information.get_file_details_dataframe()
d2_names_df = information.get_d2_names_dataframe()
information.close()

# Generate JSON
json_gen = JSONGenerator(file_details_df, d2_names_df, processed_dfs)

# Get the filename from the original PDF
pdf_filename = os.path.basename(filepath)
json_filename = os.path.splitext(pdf_filename)[0] + '.json'

# Save JSON to current directory
json_gen.save_json(json_filename)

print(f"JSON file '{json_filename}' has been created in the current directory.")