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
    def drop_first_last(df)->pd.DataFrame:
        return df.iloc[1:-1].reset_index(drop=True)
    
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
    def fix_rows(df)->pd.DataFrame:
        pass
    
    @classmethod
    def process(cls, df):
        """
        Processes the inputted Dataframe using static methods.
        """
        # can be done in any order
        df = cls.rename_headers(df=df)
        df = cls.drop_first_last(df=df)

        # Must be done in order in this section
        #df = cls.cleanup_function_name_column(df=df)
        df = cls.function_column_combine(df=df)
        df = cls.fix_IO_column(df=df)
        df = cls.fix_wire_and_parameter_column(df=df)
        return df