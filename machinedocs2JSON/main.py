from pdf_extractor import PDFTableExtractor
from data_processor import DataFrameProcessor
import pandas as pd

pd.set_option('display.max_rows',100)

extractor = PDFTableExtractor("C:\\Users\\achabris\\desktop\\26553-HXM02-EXCAVATOR-1.24.05.2701 1.pdf", '2,3')
tables = extractor.extract_tables()

df = tables[0].df
df = DataFrameProcessor.process(df=df)
print(df)