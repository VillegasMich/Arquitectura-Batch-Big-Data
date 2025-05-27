from io import StringIO
import json
import pandas as pd
from typing import Dict
from api_requester import APIRequester
import matplotlib.pyplot as plt


def main():
    gateway_requester = APIRequester(
        "https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod"
    )
    response = gateway_requester.get("/extract-trusted-info")
    inner_dict: Dict = dict(json.loads(response["body"]))

    for path, contents in inner_dict.items():
        path = path.replace("/", "_")

        csv_io = StringIO(contents)
        df = pd.read_csv(csv_io)

        # print(df.head())

        # Clean-up just in case
        df["TIME_PERIOD"] = df["TIME_PERIOD"].astype(int)
        df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

        # Top 10 most OBS_VALUE
        top10 = df.sort_values(by="OBS_VALUE", ascending=False).head(10)
        plt.figure(figsize=(10, 6))
        plt.bar(top10["REF_AREA"], top10["OBS_VALUE"], color="skyblue")
        plt.title("Top 10 Countries by OBS_VALUE in 1990")
        plt.xlabel("Country (REF_AREA)")
        plt.ylabel("Observed Value")
        plt.xticks(rotation=45)
        plt.tight_layout()
        # plt.show()
        plt.savefig(f"top10_countries_by_obs_value_{path}.png")

        # Histogram OBS_VALUE
        plt.figure(figsize=(8, 5))
        plt.hist(df["OBS_VALUE"].dropna(), bins=20, color="salmon", edgecolor="black")
        plt.title("Distribution of OBS_VALUE")
        plt.xlabel("Observed Value")
        plt.ylabel("Frequency")
        plt.tight_layout()
        # plt.show()
        plt.savefig(f"histogram_obs_value_{path}.png")


if __name__ == "__main__":
    main()
