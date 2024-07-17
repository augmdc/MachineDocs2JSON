import os
import re
from multiprocessing import Pool, cpu_count
from pdf_extractor import PDFTableExtractor
from data_processor import DataFrameProcessor
from extract_file_info import FileInformationExtractor
from json_formatter import JSONGenerator
import pandas as pd

def process_pdf(args):
    filepath, output_folder = args
    try:
        print(f"Processing file: {filepath}")
        
        information = FileInformationExtractor(file_path=filepath)
        number_of_d2_pages = information.get_number_of_d2_pages()

        pages_to_extract = ','.join(str(i) for i in range(2, 2 + number_of_d2_pages))

        extractor = PDFTableExtractor(file_path=filepath, pages_to_extract_from=pages_to_extract)
        tables = extractor.extract_tables()

        processed_dfs = DataFrameProcessor.process_multiple([table.df for table in tables])

        information.extract_text_to_dataframes()
        file_details_df = information.get_file_details_dataframe()
        d2_names_df = information.get_d2_names_dataframe()
        information.close()

        json_gen = JSONGenerator(file_details_df, d2_names_df, processed_dfs)

        pdf_filename = os.path.basename(filepath)
        json_filename = os.path.splitext(pdf_filename)[0] + '.json'
        json_filepath = os.path.join(output_folder, json_filename)

        json_gen.save_json(json_filepath)

        print(f"JSON file '{json_filename}' has been created in the output folder.")
        return f"Successfully processed {filepath}\n"
    except Exception as e:
        return f"Error processing file {filepath}: {str(e)}"

def main():
    input_folder = "C:\\Users\\achabris\\desktop\\input_pdfs"
    output_folder = "C:\\Users\\achabris\\desktop\\output_jsons"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [
        (os.path.join(input_folder, filename), output_folder)
        for filename in os.listdir(input_folder)
    ]

    # Determine the number of processes to use
    num_processes = min(cpu_count(), len(pdf_files))

    # Create a pool of worker processes
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_pdf, pdf_files)

    # Print results
    for result in results:
        print(result)

if __name__ == "__main__":
    pd.set_option('display.max_rows', 100)
    main()