import PyPDF2

class PDFExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pdf_reader = None
        self.file = None

    def open_pdf(self):
        try:
            self.file = open(self.file_path, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(self.file)
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            raise
        except PyPDF2.errors.PdfReadError:
            print("Error: Invalid PDF file")
            raise

    def extract_text_by_line(self):
        if not self.pdf_reader:
            self.open_pdf()
        
        all_lines = []
        for page in self.pdf_reader.pages[1:]:
            text = page.extract_text()
            lines = text.split('\n')
            # Remove empty lines and strip whitespace
            lines = [line.strip() for line in lines if line.strip()]
            all_lines.extend(lines)
        
        return all_lines

    def close(self):
        if self.file:
            self.file.close()
        self.pdf_reader = None
        self.file = None