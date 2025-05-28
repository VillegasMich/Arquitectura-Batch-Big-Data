from io import StringIO
import json
import pandas as pd
from typing import Dict
from api_requester import APIRequester
import matplotlib.pyplot as plt


def main():
    dataframes = []

    gateway_requester = APIRequester(
        "https://pl4uky6vwj.execute-api.us-east-1.amazonaws.com/prod"
    )
    response = gateway_requester.get("/extract-trusted-info")
    inner_dict: Dict = dict(json.loads(response["body"]))

    for path, contents in inner_dict.items():
        print(path)

        csv_io = StringIO(contents)
        df = pd.read_csv(csv_io)

        dataframes.append(df)

    stats_country_global_df: pd.DataFrame = dataframes[0]
    stats_country_indicator_ESG_df: pd.DataFrame = dataframes[1]
    stats_country_indicator_SE4ALL_df: pd.DataFrame = dataframes[2]
    stats_country_indicator_WDI_df: pd.DataFrame = dataframes[3]

    """
    GLOBAL STATS
    - Gran variabilidad
    - Gran diferencia entre el min y max indican potenciales puntos de inflación
    """
    # print(stats_country_global_df.head())
    plt.figure(figsize=(14, 6))
    plt.plot(
        stats_country_global_df["REF_AREA"],
        stats_country_global_df["mean_obs"],
        label="Mean",
        marker="o",
    )
    plt.plot(
        stats_country_global_df["REF_AREA"],
        stats_country_global_df["median_obs"],
        label="Median",
        marker="x",
    )
    plt.plot(
        stats_country_global_df["REF_AREA"],
        stats_country_global_df["min_obs"],
        label="Min",
        linestyle="--",
    )
    plt.plot(
        stats_country_global_df["REF_AREA"],
        stats_country_global_df["max_obs"],
        label="Max",
        linestyle="--",
    )
    plt.title("Observation Statistics by REF_AREA")
    plt.xlabel("REF_AREA")
    plt.ylabel("Observation Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    step = 5
    plt.xticks(
        ticks=range(0, len(stats_country_global_df["REF_AREA"]), step),
        labels=stats_country_global_df["REF_AREA"][::step],
        rotation=45,
        ha="right",
    )
    plt.savefig("results/observation_statis_country_global.png")

    """
    🌱 ESG — Environmental, Social, and Governance
        Sustainability and ethical performance
    """
    # print(stats_country_indicator_ESG_df.head())
    df = stats_country_indicator_ESG_df
    plt.figure(figsize=(14, 6))  # Wider figure
    plt.plot(df["REF_AREA"], df["avg_val"], label="Average", marker="o")
    plt.plot(df["REF_AREA"], df["median_val"], label="Median", marker="x")
    plt.plot(df["REF_AREA"], df["min_val"], label="Min", linestyle="--")
    plt.plot(df["REF_AREA"], df["max_val"], label="Max", linestyle="--")
    plt.title("Observation Summary Statistics by REF_AREA")
    plt.xlabel("REF_AREA")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    # Rotate x-axis labels
    step = 5
    plt.xticks(
        ticks=range(0, len(df["REF_AREA"]), step),
        labels=df["REF_AREA"][::step],
        rotation=45,
        ha="right",
    )

    plt.tight_layout()
    plt.savefig("results/observation_summary_stats_ESG.png")

    """
    ⚡ SE4ALL — Sustainable Energy for All
        Energy access, efficiency, renewables
    """
    # print(stats_country_indicator_SE4ALL_df.head())
    df = stats_country_indicator_SE4ALL_df
    plt.figure(figsize=(14, 6))  # Wider figure
    plt.plot(df["REF_AREA"], df["avg_val"], label="Average", marker="o")
    plt.plot(df["REF_AREA"], df["median_val"], label="Median", marker="x")
    plt.plot(df["REF_AREA"], df["min_val"], label="Min", linestyle="--")
    plt.plot(df["REF_AREA"], df["max_val"], label="Max", linestyle="--")
    plt.title("Observation Summary Statistics by REF_AREA")
    plt.xlabel("REF_AREA")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    # Rotate x-axis labels
    step = 5
    plt.xticks(
        ticks=range(0, len(df["REF_AREA"]), step),
        labels=df["REF_AREA"][::step],
        rotation=45,
        ha="right",
    )

    plt.tight_layout()
    plt.savefig("results/observation_summary_stats_SE4ALL.png")

    """
    🌍 WDI — World Development Indicators (World Bank)
        General economic, social, and development metrics
    """
    # print(stats_country_indicator_WDI_df.head())
    df = stats_country_indicator_WDI_df
    plt.figure(figsize=(14, 6))  # Wider figure
    plt.plot(df["REF_AREA"], df["avg_val"], label="Average", marker="o")
    plt.plot(df["REF_AREA"], df["median_val"], label="Median", marker="x")
    plt.plot(df["REF_AREA"], df["min_val"], label="Min", linestyle="--")
    plt.plot(df["REF_AREA"], df["max_val"], label="Max", linestyle="--")
    plt.title("Observation Summary Statistics by REF_AREA")
    plt.xlabel("REF_AREA")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)

    # Rotate x-axis labels
    step = 5
    plt.xticks(
        ticks=range(0, len(df["REF_AREA"]), step),
        labels=df["REF_AREA"][::step],
        rotation=45,
        ha="right",
    )

    plt.tight_layout()
    plt.savefig("results/observation_summary_stats_WDI.png")


if __name__ == "__main__":
    main()
