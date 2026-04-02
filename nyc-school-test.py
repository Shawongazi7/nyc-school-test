from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path("schools.csv")
FINDINGS_DIR = Path("key-findings")
PLOTS_DIR = Path("plots")
MAX_SAT_SECTION_SCORE = 800
TOP_N_SCHOOLS = 10


def load_school_data(path: Path) -> pd.DataFrame:
    """Load and clean the NYC school SAT dataset."""
    schools = pd.read_csv(path)

    numeric_columns = [
        "average_math",
        "average_reading",
        "average_writing",
        "percent_tested",
    ]
    for column in numeric_columns:
        schools[column] = pd.to_numeric(schools[column], errors="coerce")

    schools["total_SAT"] = (
        schools["average_math"]
        + schools["average_reading"]
        + schools["average_writing"]
    )

    return schools


def get_best_math_schools(schools: pd.DataFrame) -> pd.DataFrame:
    threshold = 0.8 * MAX_SAT_SECTION_SCORE
    best_math_schools = (
        schools.loc[schools["average_math"] >= threshold, ["school_name", "borough", "average_math"]]
        .sort_values(["average_math", "school_name"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return best_math_schools


def get_top_10_schools(schools: pd.DataFrame) -> pd.DataFrame:
    top_schools = (
        schools.loc[
            :,
            [
                "school_name",
                "borough",
                "average_math",
                "average_reading",
                "average_writing",
                "total_SAT",
            ],
        ]
        .sort_values(["total_SAT", "school_name"], ascending=[False, True])
        .head(TOP_N_SCHOOLS)
        .reset_index(drop=True)
    )
    return top_schools


def get_borough_performance(schools: pd.DataFrame) -> pd.DataFrame:
    borough_performance = (
        schools.groupby("borough", dropna=False)
        .agg(
            num_schools=("school_name", "count"),
            average_math=("average_math", "mean"),
            average_reading=("average_reading", "mean"),
            average_writing=("average_writing", "mean"),
            average_total_SAT=("total_SAT", "mean"),
            median_total_SAT=("total_SAT", "median"),
            std_total_SAT=("total_SAT", "std"),
            average_percent_tested=("percent_tested", "mean"),
        )
        .round(2)
        .sort_values("average_total_SAT", ascending=False)
        .reset_index()
    )
    return borough_performance


def get_largest_std_dev(borough_performance: pd.DataFrame) -> pd.DataFrame:
    return borough_performance.nlargest(1, "std_total_SAT").reset_index(drop=True)


def create_top_schools_plot(top_10_schools: pd.DataFrame) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_data = top_10_schools.sort_values("total_SAT")

    ax.barh(plot_data["school_name"], plot_data["total_SAT"], color="#1f77b4")
    ax.set_title("Top 10 NYC Schools by Total SAT Score", fontsize=15, pad=12)
    ax.set_xlabel("Total SAT Score")
    ax.set_ylabel("School")

    for index, value in enumerate(plot_data["total_SAT"]):
        ax.text(value + 8, index, str(int(value)), va="center", fontsize=9)

    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "top_10_total_sat.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def create_borough_plot(borough_performance: pd.DataFrame) -> None:
    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_data = borough_performance.sort_values("average_total_SAT")

    ax.bar(plot_data["borough"], plot_data["average_total_SAT"], color="#2a9d8f")
    ax.set_title("Average Total SAT Score by Borough", fontsize=15, pad=12)
    ax.set_xlabel("Borough")
    ax.set_ylabel("Average Total SAT")

    for idx, value in enumerate(plot_data["average_total_SAT"]):
        ax.text(idx, value + 8, f"{value:.0f}", ha="center", fontsize=9)

    plt.tight_layout()
    fig.savefig(PLOTS_DIR / "borough_average_sat.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    schools: pd.DataFrame,
    best_math_schools: pd.DataFrame,
    top_10_schools: pd.DataFrame,
    borough_performance: pd.DataFrame,
    largest_std_dev: pd.DataFrame,
) -> None:
    top_school = top_10_schools.iloc[0]
    top_borough = borough_performance.iloc[0]
    most_variable_borough = largest_std_dev.iloc[0]

    summary = f"""# NYC School SAT Analysis Summary

## Dataset Snapshot
- Schools analyzed: {len(schools)}
- Boroughs covered: {schools['borough'].nunique()}
- Average total SAT across all schools: {schools['total_SAT'].mean():.2f}
- Median percent tested: {schools['percent_tested'].median():.2f}

## Key Findings
1. **Top school overall**: {top_school['school_name']} ({top_school['borough']}) with a total SAT score of {int(top_school['total_SAT'])}.
2. **Strong math performers**: {len(best_math_schools)} schools scored at least 640 in average math.
3. **Top borough by average SAT**: {top_borough['borough']} with an average total SAT of {top_borough['average_total_SAT']:.2f}.
4. **Largest score variation**: {most_variable_borough['borough']} had the highest total SAT standard deviation at {most_variable_borough['std_total_SAT']:.2f}.

## Generated Assets
- `key-findings/best_math_schools.csv`
- `key-findings/top_10_schools.csv`
- `key-findings/borough_performance.csv`
- `key-findings/largest_std_dev.csv`
- `plots/top_10_total_sat.png`
- `plots/borough_average_sat.png`
"""

    (FINDINGS_DIR / "summary.md").write_text(summary, encoding="utf-8")


def save_outputs(
    best_math_schools: pd.DataFrame,
    top_10_schools: pd.DataFrame,
    borough_performance: pd.DataFrame,
    largest_std_dev: pd.DataFrame,
) -> None:
    FINDINGS_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    best_math_schools.to_csv(FINDINGS_DIR / "best_math_schools.csv", index=False)
    top_10_schools.to_csv(FINDINGS_DIR / "top_10_schools.csv", index=False)
    borough_performance.to_csv(FINDINGS_DIR / "borough_performance.csv", index=False)
    largest_std_dev.to_csv(FINDINGS_DIR / "largest_std_dev.csv", index=False)


def main() -> None:
    schools = load_school_data(DATA_PATH)

    best_math_schools = get_best_math_schools(schools)
    top_10_schools = get_top_10_schools(schools)
    borough_performance = get_borough_performance(schools)
    largest_std_dev = get_largest_std_dev(borough_performance)

    save_outputs(
        best_math_schools=best_math_schools,
        top_10_schools=top_10_schools,
        borough_performance=borough_performance,
        largest_std_dev=largest_std_dev,
    )
    create_top_schools_plot(top_10_schools)
    create_borough_plot(borough_performance)
    write_summary(
        schools=schools,
        best_math_schools=best_math_schools,
        top_10_schools=top_10_schools,
        borough_performance=borough_performance,
        largest_std_dev=largest_std_dev,
    )

    print("Analysis complete.")
    print(f"Best math schools: {len(best_math_schools)}")
    print(f"Top overall school: {top_10_schools.iloc[0]['school_name']}")
    print(f"Most variable borough: {largest_std_dev.iloc[0]['borough']}")


if __name__ == "__main__":
    main()
