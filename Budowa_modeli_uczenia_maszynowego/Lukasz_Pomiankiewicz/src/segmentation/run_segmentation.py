import mlflow
import pandas as pd

from src.data.load_data import load_data
from src.features.preprocessing import preprocess_data
from src.segmentation.kmeans import run_segmentation
from src.segmentation.profiling import profile_segments


def main():
    df = load_data()
    df = preprocess_data(df)

    mlflow.set_experiment("customer-segmentation")

    with mlflow.start_run():
        _, segmented_df, scores = run_segmentation(df)

        print("Silhouette scores:")
        for k, score in scores.items():
            print(f"k={k}: {score:.4f}")

        print("\nSegment sizes:")
        print(segmented_df["segment"].value_counts().sort_index())

        print("\nSelected clusters:")
        print(
            segmented_df.groupby("segment")[
                ["tenure", "MonthlyCharges", "TotalCharges"]
            ].mean()
        )

        print("\nChurn rate by segment:")
        print(
            segmented_df.groupby("segment")["Churn"]
            .apply(lambda x: (x == "Yes").mean())
        )

        print("\nSegment profile:")
        segment_profile = profile_segments(segmented_df)
        print(segment_profile)

        print("\nContract by segment:")
        print(
            pd.crosstab(
                segmented_df["segment"],
                segmented_df["Contract"],
                normalize="index",
            )
        )


if __name__ == "__main__":
    main()