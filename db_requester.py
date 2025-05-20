import csv
import os
from datetime import datetime
from typing import Optional, Any
import mysql.connector


class DBRequester:
    def __init__(
        self,
        host: str,
        port: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        output_dir: str = "./csv_outputs",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_info_from_table(self, table_name: str) -> Any:
        conn = None
        cursor = None
        results = None
        table_headers = None

        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
            )

            cursor = conn.cursor()
            sql_query = f"SELECT * FROM {table_name};"
            cursor.execute(sql_query)
            table_headers = cursor.description

            results = cursor.fetchall()

        except Exception as e:
            print(f"Database error: {e}")
            results = None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return results, table_headers

    def export_table_to_csv(self, table_name: str, filename: str):
        data, table_headers = self.get_info_from_table(table_name)

        if data is None:
            print(
                f"Failed to retrieve data from table '{table_name}'. Cannot create CSV."
            )
            return False

        if not data:
            print(f"No data found in table '{table_name}'.")
            return False

        output_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.writer(csvfile)

                headers = [i[0] for i in table_headers]
                csv_writer.writerow(headers)

                for row in data:
                    processed_row = [
                        item.isoformat() if isinstance(item, datetime) else item
                        for item in row
                    ]
                    csv_writer.writerow(processed_row)

            print(f"✅ CSV file created: {output_path}")
            return output_path, filename

        except IOError as e:
            print(f"❌ Failed to write CSV file: {e}")
            raise
        except Exception as e:
            print(f"❌ Failed to write CSV file: {e}")
            raise
