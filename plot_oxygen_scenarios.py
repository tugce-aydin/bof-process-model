import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------
# LOAD SCENARIO DATA
# -------------------------------------------------

low = pd.read_csv("results/oxygen_250.csv")
base = pd.read_csv("results/oxygen_300.csv")
high = pd.read_csv("results/oxygen_350.csv")


# -------------------------------------------------
# 1. CARBON COMPARISON
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    low["time_s"],
    low["carbon_wt_pct"],
    label="250 Nm³/min"
)

plt.plot(
    base["time_s"],
    base["carbon_wt_pct"],
    label="300 Nm³/min"
)

plt.plot(
    high["time_s"],
    high["carbon_wt_pct"],
    label="350 Nm³/min"
)

plt.xlabel("Time (s)")
plt.ylabel("Carbon (wt.%)")
plt.title("Effect of Oxygen Flow on Carbon Content")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "results/oxygen_carbon_comparison.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 2. TEMPERATURE COMPARISON
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    low["time_s"],
    low["temperature_C"],
    label="250 Nm³/min"
)

plt.plot(
    base["time_s"],
    base["temperature_C"],
    label="300 Nm³/min"
)

plt.plot(
    high["time_s"],
    high["temperature_C"],
    label="350 Nm³/min"
)

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Effect of Oxygen Flow on Bath Temperature")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "results/oxygen_temperature_comparison.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 3. SCRAP MELTING COMPARISON
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    low["time_s"],
    low["melted_scrap_kg"],
    label="250 Nm³/min"
)

plt.plot(
    base["time_s"],
    base["melted_scrap_kg"],
    label="300 Nm³/min"
)

plt.plot(
    high["time_s"],
    high["melted_scrap_kg"],
    label="350 Nm³/min"
)

plt.xlabel("Time (s)")
plt.ylabel("Melted Scrap (kg)")
plt.title("Effect of Oxygen Flow on Scrap Melting")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "results/oxygen_scrap_comparison.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 4. CO PRODUCTION COMPARISON
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    low["time_s"],
    low["CO_kg"],
    label="250 Nm³/min"
)

plt.plot(
    base["time_s"],
    base["CO_kg"],
    label="300 Nm³/min"
)

plt.plot(
    high["time_s"],
    high["CO_kg"],
    label="350 Nm³/min"
)

plt.xlabel("Time (s)")
plt.ylabel("Cumulative CO (kg)")
plt.title("Effect of Oxygen Flow on CO Production")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    "results/oxygen_CO_comparison.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# FINAL VALUES
# -------------------------------------------------

print()
print("=== OXYGEN FLOW SCENARIO COMPARISON ===")
print()

for flow, data in [
    (250, low),
    (300, base),
    (350, high)
]:
    final = data.iloc[-1]

    print(
        f"{flow} Nm³/min | "
        f"C = {final['carbon_wt_pct']:.3f} wt.% | "
        f"T = {final['temperature_C']:.1f} °C | "
        f"Melted scrap = {final['melted_scrap_kg']:.1f} kg | "
        f"CO = {final['CO_kg']:.1f} kg"
    )


print()
print("Scenario plots generated successfully.")