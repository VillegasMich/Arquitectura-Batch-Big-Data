import schedule
import time
import random
from api_requester import APIRequester
from data_pool import DATA_POOL_MAX_LENGTH, SAKILA_POOL, WORLD_BANK_POOL
from db_requester import DBRequester
from json_csv_converter import JSONToCSVConverter
from s3_upload_files import S3Uploader


def main():
    files = []
    data_pool_pos = random.randint(0, DATA_POOL_MAX_LENGTH - 1)

    # Fetch Sakila DB
    sakila_table_name = SAKILA_POOL[data_pool_pos]
    db_sakila_client = DBRequester("127.0.0.1", "3306", "root", "sakila", "sakila")
    csv_file_sk, csv_filename_sk = db_sakila_client.export_table_to_csv(
        table_name=sakila_table_name, filename="sakila_" + sakila_table_name + ".csv"
    )

    files.append((csv_file_sk, csv_filename_sk))

    # Fetch API
    worldbank_client = APIRequester("https://data360api.worldbank.org")

    # Get response in memory
    worldbank_database_id = WORLD_BANK_POOL[data_pool_pos]
    response = worldbank_client.get(
        "/data360/data", {"DATABASE_ID": worldbank_database_id}
    )

    # Get and save JSON file
    json_file, json_filename = worldbank_client.get_and_save_file(
        path="/data360/data",
        filename=worldbank_database_id + ".json",
        params={"DATABASE_ID": worldbank_database_id},
    )

    files.append((json_file, json_filename))

    # Step 2: Convert response to CSV
    converter = JSONToCSVConverter()
    csv_file_wb, csv_filename_wb = converter.convert_from_worldbank(
        api_response=response, filename=worldbank_database_id + ".csv"
    )

    files.append((csv_file_wb, csv_filename_wb))

    # Step 3: Upload files to S3
    for file_path, filename in files:
        S3Uploader.upload_file_to_public_s3(
            file_path,
            S3Uploader.AWS_BUCKET_NAME,
            filename,
            S3Uploader.AWS_ACCESS_KEY,
            S3Uploader.AWS_SECRET_KEY,
            S3Uploader.AWS_SESSION_TOKEN,
        )

    print("30 minutes timeout...")


# Schedule to run every 30 minutes
schedule.every(30).minutes.do(main)


if __name__ == "__main__":
    print("Scheduler started.")
    main()
    while True:
        schedule.run_pending()
        time.sleep(1)
