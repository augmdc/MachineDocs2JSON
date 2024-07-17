import camelot

class PDFTableExtractor:
    def __init__(self, file_path, pages_to_extract_from):
        self.file_path = file_path
        self.pages_to_extract_from = pages_to_extract_from

    def extract_tables(self):
        return camelot.read_pdf(
            filepath=self.file_path,
            pages=self.pages_to_extract_from
            )