import json
import pandas as pd
import re

class JSONGenerator:
    def __init__(self, file_details_df, d2_names_df, d2_details_dfs):
        self.file_details_df = file_details_df
        self.d2_names_df = d2_names_df
        self.d2_details_dfs = d2_details_dfs if isinstance(d2_details_dfs, list) else [d2_details_dfs]

    def sanitize_io(self, io_value):
        if pd.isna(io_value) or io_value == '-':
            return ''
        # Remove any numerical values and trailing spaces from I/O
        return re.sub(r'\s*\d+(\.\d+)?\s*', '', io_value).strip()

    def process_pin_type(self, type_value, io_value):
        if pd.isna(type_value) or type_value == '-':
            type_value = ''
        
        sanitized_io = self.sanitize_io(io_value)
        
        # Combine type and sanitized I/O
        combined_type = f"{type_value}_{sanitized_io}".upper().strip('_')
        
        # Simplify LED types
        if combined_type.startswith('LED'):
            return 'LED'
        
        # Process PWM types
        if combined_type.startswith('PWM'):
            pwm_match = re.search(r'(\d+)\s*HZ', type_value, re.IGNORECASE)
            if pwm_match:
                return 'PWM', int(pwm_match.group(1))
            return 'PWM'
        
        return combined_type

    def generate_json(self):
        if self.file_details_df.empty:
            raise ValueError("File details DataFrame is empty")

        file_details = self.file_details_df.iloc[0]  # Assuming there's only one row

        base_structure = {
            "Machine": file_details.get('Machine', ''),
            "type": file_details.get('type', ''),
            "printDate": file_details.get('printed_date', ''),
            "INVID": int(file_details.get('INVID', 0)),
            "D02s": []
        }

        # Process D2 names and details
        for idx, d2_row in self.d2_names_df.iterrows():
            d2_name = d2_row['D2_name']
            d2_structure = {"name": d2_name}
            
            # Ensure we have a corresponding DataFrame for this D2
            if idx < len(self.d2_details_dfs):
                d2_details_df = self.d2_details_dfs[idx]
                
                current_section = None
                for _, row in d2_details_df.iterrows():
                    pin = row['Pin']
                    
                    if re.match(r'CON\d+', pin):
                        current_section = pin
                        d2_structure[current_section] = {}
                    elif pin.startswith("D28 RISER CARD"):
                        if "RIGHT" in pin:
                            current_section = "D28_RISER_RIGHT"
                        elif "LEFT" in pin:
                            current_section = "D28_RISER_LEFT"
                        else:
                            current_section = "D28_RISER"
                        d2_structure[current_section] = {}
                    elif current_section and pd.notna(pin):
                        # Process Type and I/O
                        pin_type = self.process_pin_type(row['Type'], row['I/O'])
                        
                        pin_data = {}
                        if isinstance(pin_type, tuple):
                            pin_data["type"] = pin_type[0]
                            pin_data["frequency"] = pin_type[1]
                        elif pin_type:
                            pin_data["type"] = pin_type
                        
                        # Handle Function Name
                        if isinstance(row['Function Name'], list) and row['Function Name']:
                            valid_functions = [f for f in row['Function Name'] if f != '-']
                            if valid_functions:
                                pin_data["functionName"] = valid_functions[0]
                                if len(valid_functions) > 1:
                                    pin_data["alternateNames"] = valid_functions[1:]
                        
                        if pin_data:  # Only add the pin if it has any data
                            # Remove the leading dot from pin names
                            clean_pin = pin.lstrip('.')
                            d2_structure[current_section][clean_pin] = pin_data

            # Only add the D2 structure if it has any content beyond the name
            if len(d2_structure) > 1:
                base_structure["D02s"].append(d2_structure)

        return base_structure

    def save_json(self, filename):
        json_data = self.generate_json()
        
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"JSON file '{filename}' has been created successfully.")