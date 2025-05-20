import schedule
import time
from api_requester import APIRequester
from db_requester import DBRequester
from json_csv_converter import JSONToCSVConverter
from s3_upload_files import S3Uploader


def main():
    # Fetch Sakila DB
    db_sakila_client = DBRequester("127.0.0.1", "3306", "root", "sakila", "sakila")
    csv_file_sk, csv_filename_sk = db_sakila_client.export_table_to_csv(
        table_name="actor", filename="sakila_actor.csv"
    )

    # Fetch API
    worldbank_client = APIRequester("https://data360api.worldbank.org")

    # Get response in memory
    response = worldbank_client.get("/data360/data", {"DATABASE_ID": "WB_MPM"})

    # Get and save JSON file
    json_file, json_filename = worldbank_client.get_and_save_file(
        path="/data360/data",
        filename="WB_MPM.json",
        params={"DATABASE_ID": "WB_MPM"},
    )

    # Step 2: Convert response to CSV
    converter = JSONToCSVConverter()
    csv_file_wb, csv_filename_wb = converter.convert_from_worldbank(
        api_response=response, filename="WB_MPM.csv"
    )

    # Step 3: Upload files to S3
    for file_path, filename in [
        (csv_file_wb, csv_filename_wb),
        (csv_file_sk, csv_filename_sk),
        (json_file, json_filename),
    ]:
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
