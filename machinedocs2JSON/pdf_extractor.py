import PyPDF2
import re

class PDFExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_reader = None
        self.file = None

    def open_pdf(self):
        try:
            self.file = open(self.file_path, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(self.file)
            print(f"Successfully opened PDF. Total pages: {len(self.pdf_reader.pages)}")
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            raise
        except PyPDF2.errors.PdfReadError:
            print("Error: Invalid PDF file")
            raise

    def extract_text(self):
        if not self.pdf_reader:
            self.open_pdf()
        
        all_content = []
        confidential_statements = [
            "CONFIDENTIAL. DO NOT DISTRIBUTE.",
            "FOR HLS HARD-LINE SOLUTIONS INTERNAL USE ONLY."
        ]
        pattern = r'(CON\d+\s*.*?)(?=CON\d+|$)'
        
        for page_num, page in enumerate(self.pdf_reader.pages[1:2], 2):
            print(f"Processing page {page_num}")
            text = page.extract_text()
            #TO-DO: separate out all of the text by grouping them into a dictionary with CONX as the key and the text as the value
            con_dict = dict()
            captured_conn_groups = []

            """
            matches = re.findall(pattern, text, re.DOTALL)
            matches = [f"Item {i}:" + item for i, item in enumerate(matches)]
            for item in matches:
                print(item)
            """
            
            lines = text.split('\n')
            
            if lines and any(line.strip().startswith("D2") for line in lines):
                print(f"Found D2 on page {page_num}")
                page_content = [line.strip() for line in lines if line.strip() and not any(stmt in line for stmt in confidential_statements)]

                all_content.extend(page_content)
            else:
                print(f"No D2 found on page {page_num}")
        
        print(f"Total lines extracted: {len(all_content)}")
        return all_content
        
            
    

    def close(self):
        if self.file:
            self.file.close()
        self.pdf_reader = None
        self.file = None