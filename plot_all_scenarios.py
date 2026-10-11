import pandas as pd
import matplotlib.pyplot as plt


# =================================================
# HELPER FUNCTIONS
# =================================================

def load(path):
    return pd.read_csv(path)


def full_melting_time(data, total_scrap):
    melted = data[data["melted_scrap_kg"] >= total_scrap - 0.1]

    if melted.empty:
        return None

    return melted.iloc[0]["time_s"]


def print_final_result(name, data, total_scrap):
    final = data.iloc[-1]
    melting_time = full_melting_time(data, total_scrap)

    if melting_time is None:
        melting_text = "not fully melted"
    else:
        melting_text = f"{melting_time:.0f} s"

    print(
        f"{name:<18} | "
        f"C = {final['carbon_wt_pct']:.3f} wt.% | "
        f"T = {final['temperature_C']:.1f} °C | "
        f"CO = {final['CO_kg']:.1f} kg | "
        f"Full melt = {melting_text}"
    )


def plot_comparison(
    datasets,
    column,
    ylabel,
    title,
    filename
):
    plt.figure(figsize=(9, 5))

    for label, data in datasets:
        plt.plot(
            data["time_s"],
            data[column],
            label=label
        )

    plt.xlabel("Time (s)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        f"results/{filename}",
        dpi=300
    )

    plt.close()


# =================================================
# LOAD OXYGEN SCENARIOS
# =================================================

oxygen250 = load("results/oxygen_250.csv")
oxygen300 = load("results/oxygen_300.csv")
oxygen350 = load("results/oxygen_350.csv")

oxygen_data = [
    ("250 Nm³/min", oxygen250),
    ("300 Nm³/min", oxygen300),
    ("350 Nm³/min", oxygen350)
]


# =================================================
# LOAD SCRAP SCENARIOS
# =================================================

scrap10000 = load("results/scrap_10000.csv")
scrap15000 = load("results/scrap_15000.csv")
scrap20000 = load("results/scrap_20000.csv")

scrap_data = [
    ("10,000 kg", scrap10000),
    ("15,000 kg", scrap15000),
    ("20,000 kg", scrap20000)
]


# =================================================
# LOAD INITIAL TEMPERATURE SCENARIOS
# =================================================

temperature1300 = load("results/temperature_1300.csv")
temperature1350 = load("results/temperature_1350.csv")
temperature1400 = load("results/temperature_1400.csv")

temperature_data = [
    ("1300 °C", temperature1300),
    ("1350 °C", temperature1350),
    ("1400 °C", temperature1400)
]


# =================================================
# OXYGEN FLOW PLOTS
# =================================================

plot_comparison(
    oxygen_data,
    "carbon_wt_pct",
    "Carbon (wt.%)",
    "Effect of Oxygen Flow on Carbon Content",
    "oxygen_carbon_comparison.png"
)

plot_comparison(
    oxygen_data,
    "temperature_C",
    "Temperature (°C)",
    "Effect of Oxygen Flow on Bath Temperature",
    "oxygen_temperature_comparison.png"
)

plot_comparison(
    oxygen_data,
    "melted_scrap_kg",
    "Melted Scrap (kg)",
    "Effect of Oxygen Flow on Scrap Melting",
    "oxygen_scrap_comparison.png"
)


# =================================================
# SCRAP MASS PLOTS
# =================================================

plot_comparison(
    scrap_data,
    "carbon_wt_pct",
    "Carbon (wt.%)",
    "Effect of Scrap Mass on Carbon Content",
    "scrap_carbon_comparison.png"
)

plot_comparison(
    scrap_data,
    "temperature_C",
    "Temperature (°C)",
    "Effect of Scrap Mass on Bath Temperature",
    "scrap_temperature_comparison.png"
)

plot_comparison(
    scrap_data,
    "melted_scrap_kg",
    "Melted Scrap (kg)",
    "Effect of Scrap Mass on Scrap Melting",
    "scrap_melting_comparison.png"
)


# =================================================
# INITIAL TEMPERATURE PLOTS
# =================================================

plot_comparison(
    temperature_data,
    "carbon_wt_pct",
    "Carbon (wt.%)",
    "Effect of Initial Temperature on Carbon Content",
    "initial_temperature_carbon_comparison.png"
)

plot_comparison(
    temperature_data,
    "temperature_C",
    "Temperature (°C)",
    "Effect of Initial Temperature on Bath Temperature",
    "initial_temperature_bath_comparison.png"
)

plot_comparison(
    temperature_data,
    "melted_scrap_kg",
    "Melted Scrap (kg)",
    "Effect of Initial Temperature on Scrap Melting",
    "initial_temperature_scrap_comparison.png"
)


# =================================================
# NUMERICAL SUMMARY
# =================================================

print()
print("============================================================")
print("OXYGEN FLOW SCENARIOS")
print("============================================================")

print_final_result(
    "250 Nm³/min",
    oxygen250,
    15000
)

print_final_result(
    "300 Nm³/min",
    oxygen300,
    15000
)

print_final_result(
    "350 Nm³/min",
    oxygen350,
    15000
)


print()
print("============================================================")
print("SCRAP MASS SCENARIOS")
print("============================================================")

print_final_result(
    "10,000 kg",
    scrap10000,
    10000
)

print_final_result(
    "15,000 kg",
    scrap15000,
    15000
)

print_final_result(
    "20,000 kg",
    scrap20000,
    20000
)


print()
print("============================================================")
print("INITIAL TEMPERATURE SCENARIOS")
print("============================================================")

print_final_result(
    "1300 °C",
    temperature1300,
    15000
)

print_final_result(
    "1350 °C",
    temperature1350,
    15000
)

print_final_result(
    "1400 °C",
    temperature1400,
    15000
)


print()
print("All scenario plots generated successfully.")