import PyPDF2
import pandas as pd
import re

class FileInformationExtractor:
    """
    Extracts file details, printed date, and D2 page names from the document and creates DataFrames
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_reader = None
        self.file = None
        self.file_details_df = None
        self.d2_names_df = None

    def open_pdf(self):
        try:
            self.file = open(self.file_path, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(self.file)
            #print(f"Successfully opened PDF. Total pages: {len(self.pdf_reader.pages)}")
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            raise
        except PyPDF2.errors.PdfReadError:
            print("Error: Invalid PDF file")
            raise

    def extract_text_to_dataframes(self):
        if not self.pdf_reader:
            self.open_pdf()
        
        # Extract file details from the first page
        first_page_text = self.pdf_reader.pages[0].extract_text()
        self.extract_file_details(first_page_text)
        
        # Extract D2 names from all pages
        self.extract_d2_names()

    def extract_file_details(self, text):
        # Regular expression to find the pattern for machine details
        pattern = r'(\d+)-(\w+)-(\w+)'
        match = re.search(pattern, text)
        
        # Regular expression to find the printed date
        date_pattern = r'Printed On [A-Za-z]+, ([A-Za-z]+ \d+, \d{4})'
        date_match = re.search(date_pattern, text)
        
        if match and date_match:
            invid, type_, machine = match.groups()
            printed_date = date_match.group(1)
            
            self.file_details_df = pd.DataFrame({
                'Machine': [machine.capitalize()],
                'type': [type_],
                'INVID': [invid],
                'printed_date': [printed_date]
            })
            #print("File details DataFrame created successfully:")
            #print(self.file_details_df)
        else:
            print("Required patterns not found in the extracted text")
            self.file_details_df = pd.DataFrame(columns=['Machine', 'type', 'INVID', 'printed_date'])

    def extract_d2_names(self):
        d2_names = []
        for page in self.pdf_reader.pages[1:]:  # Start from the second page
            text = page.extract_text()
            lines = text.split('\n')
            if lines:
                first_line = lines[0].strip()
                if first_line.startswith("D2 I/O Designations"):
                    name_match = re.search(r'- CAN[ID]* ([^*]+)\*', first_line)
                    if name_match:
                        d2_names.append(name_match.group(1))
        
        self.d2_names_df = pd.DataFrame({'D2_name': d2_names})
        #print("D2 names DataFrame created successfully:")
        #print(self.d2_names_df)

    def get_file_details_dataframe(self):
        if self.file_details_df is None:
            self.extract_text_to_dataframes()
        return self.file_details_df

    def get_d2_names_dataframe(self):
        if self.d2_names_df is None:
            self.extract_text_to_dataframes()
        return self.d2_names_df

    def get_number_of_d2_pages(self):
        if self.d2_names_df is None:
            self.extract_text_to_dataframes()
        return len(self.d2_names_df)

    def close(self):
        if self.file:
            self.file.close()
        self.pdf_reader = None
        self.file = None