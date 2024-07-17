import json
import pandas as pd
import re

class JSONGenerator:
    def __init__(self, file_details_df, d2_names_df, d2_details_dfs):
        self.file_details_df = file_details_df
        self.d2_names_df = d2_names_df
        self.d2_details_dfs = d2_details_dfs

    def generate_json(self):
        if self.file_details_df.empty:
            raise ValueError("File details DataFrame is empty")

        file_details = self.file_details_df.iloc[0]  # Assuming there's only one row

        base_structure = {
            "Machine": file_details.get('Machine', ''),
            "type": file_details.get('type', ''),
            "printed date": file_details.get('printed_date', ''),
            "INVID": int(file_details.get('INVID', 0)),
            "D02s": []
        }

        # Process D2 names and details
        for index, d2_row in self.d2_names_df.iterrows():
            d2_name = d2_row['D2_name']
            if index < len(self.d2_details_dfs):
                d2_df = self.d2_details_dfs[index]
                d2_structure = self.process_d2_dataframe(d2_name, d2_df)
                base_structure["D02s"].append(d2_structure)

        return base_structure

    def process_d2_dataframe(self, d2_name, df):
        d2_structure = {"name": d2_name}
        current_section = None

        for _, row in df.iterrows():
            pin = row['Pin']
            
            if re.match(r'CON\d+', pin) or pin.startswith("D28 RISER CARD"):
                current_section = pin
                d2_structure[current_section] = {}
            elif current_section and pd.notna(pin):
                # Handle Type and I/O
                type_value = row['Type'] if pd.notna(row['Type']) and row['Type'] != '-' else ''
                io_value = row['I/O'] if pd.notna(row['I/O']) and row['I/O'] != '-' else ''
                
                if type_value and io_value:
                    pin_type = f"{type_value}_{io_value.split()[0]}".upper()
                else:
                    pin_type = type_value.upper() or io_value.upper()
                
                pin_data = {"type": pin_type} if pin_type else {}
                
                # Handle Function Name
                if isinstance(row['Function Name'], list) and row['Function Name']:
                    valid_functions = [f for f in row['Function Name'] if f != '-']
                    if valid_functions:
                        pin_data["function name"] = valid_functions[0]
                        if len(valid_functions) > 1:
                            pin_data["alternate function names"] = valid_functions[1:]
                
                if pin_data:  # Only add the pin if it has any data
                    d2_structure[current_section][pin] = pin_data

        return d2_structure

    def save_json(self, filename):
        json_data = self.generate_json()
        
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"JSON file '{filename}' has been created successfully.")