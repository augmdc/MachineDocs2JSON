import os
import re
import argparse
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from pdf_extractor import PDFTableExtractor
from data_processor import DataFrameProcessor
from extract_file_info import FileInformationExtractor
from json_formatter import JSONGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('pdf_processor.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def process_pdf(args):
    filepath, output_folder = args
    try:
        logger.info(f"Processing file: {filepath}")
        
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

        logger.info(f"JSON file '{json_filename}' has been created in the output folder.")
        return f"Successfully processed {filepath}"
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return f"Error: File not found - {filepath}"
    except Exception as e:
        logger.exception(f"Unexpected error processing {filepath}: {str(e)}")
        return f"Error processing file {filepath}: {str(e)}"

def process_pdfs_with_progress(pdf_files, num_processes):
    with Pool(processes=num_processes) as pool:
        results = list(tqdm(pool.imap(process_pdf, pdf_files), total=len(pdf_files), desc="Processing PDFs"))
    return results

def main():
    parser = argparse.ArgumentParser(description="Process PDF files and generate JSON output.")
    parser.add_argument("input_folder", help="Path to the folder containing input PDF files")
    parser.add_argument("output_folder", help="Path to the folder where JSON output will be saved")
    parser.add_argument("-n", "--num_processes", type=int, default=cpu_count(),
                        help=f"Number of processes to use (default: {cpu_count()})")
    
    args = parser.parse_args()

    logger.info(f"Starting PDF processing with args: {args}")

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
        logger.info(f"Created output folder: {args.output_folder}")

    # Fixed pattern for PDF files
    pattern = re.compile(r"\d+-\w+-\w+\.pdf")

    pdf_files = [
        (os.path.join(args.input_folder, filename), args.output_folder)
        for filename in os.listdir(args.input_folder)
        #if pattern.match(filename)
    ]

    if not pdf_files:
        logger.warning(f"No PDF files matching the pattern found in {args.input_folder}")
        print(f"No PDF files matching the pattern found in {args.input_folder}")
        return

    num_processes = min(args.num_processes, len(pdf_files))
    logger.info(f"Processing {len(pdf_files)} PDF files using {num_processes} processes")
    print(f"Processing {len(pdf_files)} PDF files using {num_processes} processes")

    results = process_pdfs_with_progress(pdf_files, num_processes)

    for result in results:
        print(result)
        logger.info(result)

    logger.info("PDF processing completed")

if __name__ == "__main__":
    main()