import pandas as pd

class DataFrameProcessor:
    @staticmethod
    def rename_headers(df)->pd.DataFrame:
        headers_str = df[0][0]
        new_headers = headers_str.split("\n")

        column_mapping = {
            0 : new_headers[0],
            1 : new_headers[1],
            2 : new_headers[2],
            3 : new_headers[3],
            9 : new_headers[4],
            10 : new_headers[5]
            }

        # Rename columns
        df = df.rename(columns=column_mapping)
        return df

    @staticmethod
    def drop_specific_rows(df)->pd.DataFrame:
        return df.iloc[1:-2].reset_index(drop=True)
    
    @staticmethod
    def function_column_combine(df)->pd.DataFrame:
        columns_to_combine = ['Function Name', 4, 5, 6, 7, 8]
        df['Function Name'] = df[columns_to_combine].apply(lambda row: [x for x in row if pd.notna(x) and x != ''], axis=1)
        df = df.drop(columns=[4, 5, 6, 7, 8])
        
        def split_and_extend(row):
            result = []
            for item in row:
                if isinstance(item, str) and '\n' in item:
                    result.extend(item.split('\n'))
                else:
                    result.append(item)
            return result
        
        df['Function Name'] = df['Function Name'].apply(split_and_extend)
        return df
    
    @staticmethod
    def fix_IO_column(df)->pd.DataFrame:
        df['I/O'] = df['I/O'].str.replace('Input', '')
        return df

    @staticmethod
    def fix_wire_and_parameter_column(df):
        if 'Wire' not in df.columns:
            df['Wire'] = ''

        def process_wire(value):
            if pd.isna(value):
                return []
            parts = str(value).split('\n\n')  # Split by double newline
            if len(parts) > 1:
                return parts
            else:
                single_parts = str(value).split('\n')  # Split by single newline
                return single_parts[:-1], single_parts[-1] if len(single_parts) > 1 else ''

        df['Wire'], df['Parameter'] = zip(*df['Wire'].apply(process_wire))
        
        # Ensure Wire is always a list
        df['Wire'] = df['Wire'].apply(lambda x: x if isinstance(x, list) else [x])
        
        return df

    @staticmethod
    @staticmethod
    def parse_mushed_rows(df):
        def split_row(row):
            if isinstance(row.iloc[0], str) and '\n' in row.iloc[0]:
                parts = row.iloc[0].split('\n')
                new_row = row.copy()

                # Handle special cases
                if any(keyword in parts for keyword in ['GROUND', 'POWER', '5 VOLTS']):
                    new_row['Pin'] = parts[0]  # First part as Pin
                    new_row['Type'] = parts[1] # Second part as Type
                    new_row['I/O'] = ''
                    new_row['Function Name'] = ['']
                else:
                    new_row['Pin'] = parts[0] if parts else ''
                    new_row['I/O'] = parts[1] if len(parts) > 1 else ''
                    new_row['Type'] = parts[2] if len(parts) > 2 else ''
                    # Only include up to the Function Name (4th part)
                    new_row['Function Name'] = [parts[3]] if len(parts) > 3 else ['']

                return new_row
            return row

        df_copy = df.copy()
        df_processed = df_copy.apply(split_row, axis=1)
        return df_processed
    
    @staticmethod
    def drop_specific_columns(df)->pd.DataFrame:
        df_copy = df.copy()
    
        # Drop the specified columns
        df_copy = df_copy.drop(columns=['Wire', 'Parameter'], errors='ignore')
    
        return df_copy
    
    @staticmethod
    def fix_con2_lines(df)->pd.DataFrame:
        """
        Fixes weird issues with CON2 rows having mixed up column values
        """
        if len(df) < 20:
            print("Warning: DataFrame does not have enough rows. No changes made.")
            return df
    
        # Create a copy of the DataFrame to avoid modifying the original
        df_copy = df.copy()
    
        # Modify row 17 (index 16)
        df_copy.loc[16, 'Pin'] = '.1'
        df_copy.loc[16, 'I/O'] = 'Input'
        df_copy.loc[16, 'Type'] = ''
        df_copy.loc[16, 'Function Name'] = []
    
        # Modify row 18 (index 17)
        df_copy.loc[17, 'Pin'] = '.2'
        df_copy.loc[17, 'I/O'] = 'Relay'
        df_copy.loc[17, 'Type'] = ''
        df_copy.loc[17, 'Function Name'] = []
    
        # Modify row 19 (index 18)
        df_copy.loc[18, 'Pin'] = '.3'
        df_copy.loc[18, 'I/O'] = 'Relay'
        df_copy.loc[18, 'Type'] = ''
        df_copy.loc[18, 'Function Name'] = []
    
        return df_copy
    
    @classmethod
    def process_multiple(cls, dataframes):
        """
        Processes multiple DataFrames using the static methods.
        
        Args:
        dataframes (list): A list of pandas DataFrames to process.
        
        Returns:
        list: A list of processed pandas DataFrames.
        """
        processed_dataframes = []
        for df in dataframes:
            processed_df = cls.process(df)
            processed_dataframes.append(processed_df)
        return processed_dataframes
    
    @classmethod
    def process(cls, df):
        """
        Processes the inputted Dataframe using static methods.
        """
        # Can be done in any order
        df = cls.rename_headers(df=df)
        df = cls.drop_specific_rows(df=df)

        # Must be done in order in this section
        df = cls.function_column_combine(df=df)
        df = cls.parse_mushed_rows(df=df)
        df = cls.drop_specific_columns(df=df)
        df = cls.fix_con2_lines(df)
        return df