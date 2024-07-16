import argparse
import sys
from pdf_extractor import PDFExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    args = parser.parse_args()

    extractor = PDFExtractor(args.pdf_path)
    try:
        lines = extractor.extract_text_by_line()
        for line in lines:
            print(line)
    except FileNotFoundError:
        print(f"Error: File not found at {args.pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred - {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        extractor.close()

if __name__ == "__main__":
    main()