import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


data = pd.read_csv("data/ml_dataset.csv")

# Only use simulations that successfully reached the carbon endpoint.
data = data[data["endpoint_reached"] == 1].copy()

features = [
    "hot_metal_kg",
    "scrap_kg",
    "initial_temp_C",
    "initial_C_pct",
    "initial_Si_pct",
    "initial_Mn_pct",
    "oxygen_flow_Nm3_min"
]

X = data[features]

targets = {
    "endpoint_time": data["endpoint_time_s"],
    "endpoint_temperature": data["endpoint_temp_C"]
}


def evaluate_model(name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="r2"
    )

    print(f"\n{name}")
    print(f"MAE:  {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")
    print(f"R2:   {r2:.4f}")
    print(f"5-fold CV R2: {cv_scores.mean():.4f}")

    return model


for target_name, y in targets.items():

    print("\n" + "=" * 50)
    print(f"TARGET: {target_name}")
    print("=" * 50)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    linear_model = LinearRegression()

    evaluate_model(
        "Linear Regression",
        linear_model,
        X_train,
        X_test,
        y_train,
        y_test
    )

    random_forest = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )

    random_forest = evaluate_model(
        "Random Forest",
        random_forest,
        X_train,
        X_test,
        y_train,
        y_test
    )

    joblib.dump(
        linear_model,
        f"ml/models/{target_name}_model.pkl"
    )


print("\nModels saved successfully.")