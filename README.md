# PDF to JSON Converter

This project extracts information from specific PDF files and converts it into a structured JSON format.

## Features

- Extracts file details, printed date, and D2 page names from PDFs
- Processes tables from PDF files
- Generates structured JSON output
- Supports multi-processing for efficient handling of multiple PDFs

## Requirements

- Python 3.x

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line:

```
python main.py <input_folder> <output_folder> [-p PATTERN] [-n NUM_PROCESSES]
```

- `<input_folder>`: Path to the folder containing input PDF files
- `<output_folder>`: Path to the folder where JSON output will be saved
- `-p, --pattern`: Regex pattern to match PDF filenames
- `-n, --num_processes`: Number of processes to use (default: number of CPU cores)

## Project Structure

- `main.py`: Main script to run the conversion process
- `pdf_extractor.py`: Extracts tables from PDF files
- `data_processor.py`: Processes extracted data
- `extract_file_info.py`: Extracts file details and D2 names
- `json_formatter.py`: Generates the final JSON output

## License

[Specify the license here]

## Contributing

[Add contribution guidelines if applicable]