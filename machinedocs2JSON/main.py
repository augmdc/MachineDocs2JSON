import os
import re
import argparse
from multiprocessing import Pool, cpu_count
from pdf_extractor import PDFTableExtractor
from data_processor import DataFrameProcessor
from extract_file_info import FileInformationExtractor
from json_formatter import JSONGenerator

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
    parser = argparse.ArgumentParser(description="Process PDF files and generate JSON output.")
    parser.add_argument("input_folder", help="Path to the folder containing input PDF files")
    parser.add_argument("output_folder", help="Path to the folder where JSON output will be saved")
    parser.add_argument("-p", "--pattern", 
                        help="Regex pattern to match PDF filenames (default: '\\d+-\\w+-\\w+\\.pdf')")
    parser.add_argument("-n", "--num_processes", type=int, default=cpu_count(),
                        help=f"Number of processes to use (default: {cpu_count()})")
    
    args = parser.parse_args()

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    pdf_files = [
        (os.path.join(args.input_folder, filename), args.output_folder)
        for filename in os.listdir(args.input_folder)
        if re.match(args.pattern, filename)
    ]

    if not pdf_files:
        print(f"No PDF files matching the pattern '{args.pattern}' found in {args.input_folder}")
        return

    num_processes = min(args.num_processes, len(pdf_files))
    print(f"Processing {len(pdf_files)} PDF files using {num_processes} processes")

    with Pool(processes=num_processes) as pool:
        results = pool.map(process_pdf, pdf_files)

    for result in results:
        print(result)

if __name__ == "__main__":
    main()