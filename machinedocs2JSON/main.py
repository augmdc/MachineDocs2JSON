import argparse
import sys
import json
from pdf_extractor import PDFExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    args = parser.parse_args()

    print(f"Attempting to extract text from: {args.pdf_path}")
    extractor = PDFExtractor(args.pdf_path)
    try:
        content = extractor.extract_text()
        if not content:
            print("No content was extracted from the PDF.")
        else:
            print("Extracted content:")
            for i, line in enumerate(content, 1):
                print(f"Line {i}: {line}")
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