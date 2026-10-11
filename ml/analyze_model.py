from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_DIR / "data" / "ml_dataset.csv"
MODEL_DIR = PROJECT_DIR / "ml" / "models"
RESULT_DIR = PROJECT_DIR / "ml" / "results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "hot_metal_kg",
    "scrap_kg",
    "initial_temp_C",
    "initial_C_pct",
    "initial_Si_pct",
    "initial_Mn_pct",
    "oxygen_flow_Nm3_min"
]

TARGETS = {
    "endpoint_time": "endpoint_time_s",
    "endpoint_temperature": "endpoint_temp_C"
}


data = pd.read_csv(DATA_FILE)
data = data[data["endpoint_reached"] == 1].copy()

print(f"Successful simulations: {len(data)}")


for target_name, target_column in TARGETS.items():

    print("\n" + "=" * 60)
    print(f"ANALYSIS: {target_name}")
    print("=" * 60)

    X = data[FEATURES]
    y = data[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    model_path = MODEL_DIR / f"{target_name}_model.pkl"
    model = joblib.load(model_path)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    print(f"MAE:  {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")
    print(f"R2:   {r2:.4f}")

    # Raw regression coefficients
    coefficients = pd.DataFrame({
        "feature": FEATURES,
        "coefficient": model.coef_
    })

    coefficients.to_csv(
        RESULT_DIR / f"{target_name}_coefficients.csv",
        index=False
    )

    print("\nRaw coefficients:")
    print(coefficients.to_string(index=False))

    # Standardized coefficients for comparing feature influence
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    standardized_effect = (
        model.coef_ * scaler.scale_
    )

    standardized_coefficients = pd.DataFrame({
        "feature": FEATURES,
        "standardized_effect": standardized_effect
    })

    standardized_coefficients["absolute_effect"] = (
        standardized_coefficients["standardized_effect"].abs()
    )

    standardized_coefficients = standardized_coefficients.sort_values(
        "absolute_effect",
        ascending=False
    )

    standardized_coefficients.to_csv(
        RESULT_DIR / f"{target_name}_feature_effects.csv",
        index=False
    )

    print("\nFeature effects:")
    print(
        standardized_coefficients[
            ["feature", "standardized_effect"]
        ].to_string(index=False)
    )

    # Actual vs predicted
    plt.figure(figsize=(7, 6))

    plt.scatter(
        y_test,
        predictions,
        alpha=0.7
    )

    minimum = min(y_test.min(), predictions.min())
    maximum = max(y_test.max(), predictions.max())

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--"
    )

    plt.xlabel("C++ Simulation")
    plt.ylabel("ML Prediction")
    plt.title(f"Actual vs Predicted - {target_name}")
    plt.tight_layout()

    plt.savefig(
        RESULT_DIR / f"{target_name}_actual_vs_predicted.png",
        dpi=300
    )

    plt.close()

    # Residual plot
    residuals = y_test - predictions

    plt.figure(figsize=(7, 6))

    plt.scatter(
        predictions,
        residuals,
        alpha=0.7
    )

    plt.axhline(
        y=0,
        linestyle="--"
    )

    plt.xlabel("ML Prediction")
    plt.ylabel("Residual (C++ - ML)")
    plt.title(f"Residuals - {target_name}")
    plt.tight_layout()

    plt.savefig(
        RESULT_DIR / f"{target_name}_residuals.png",
        dpi=300
    )

    plt.close()


print("\nAnalysis completed.")
print(f"Results saved to: {RESULT_DIR}")