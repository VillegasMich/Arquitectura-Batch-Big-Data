import csv
from typing import Dict
import os


class JSONToCSVConverter:
    def __init__(self, output_dir: str = "./csv_outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_from_worldbank(self, api_response: Dict, filename: str = "output.csv"):
        if "value" not in api_response:
            raise ValueError("The response does not have a 'value' field")

        data = api_response["value"]
        if not isinstance(data, list) or not data:
            raise ValueError("The field 'value' can't be empty")

        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
            else:
                raise ValueError("All 'value' elements must be dictionaries")

        fieldnames = all_keys
        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ CSV file created: {output_path}")
            return output_path, filename
        except Exception as e:
            print(f"❌ Failed to write CSV file: {e}")
            raise
