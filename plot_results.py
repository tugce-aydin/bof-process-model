import pandas as pd
import matplotlib.pyplot as plt


# -------------------------------------------------
# LOAD SIMULATION DATA
# -------------------------------------------------

data = pd.read_csv("results/simulation.csv")


# -------------------------------------------------
# 1. COMPOSITION
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    data["time_s"],
    data["carbon_wt_pct"],
    label="Carbon"
)

plt.plot(
    data["time_s"],
    data["silicon_wt_pct"],
    label="Silicon"
)

plt.plot(
    data["time_s"],
    data["manganese_wt_pct"],
    label="Manganese"
)

plt.xlabel("Time (s)")
plt.ylabel("Composition (wt.%)")
plt.title("BOF Bath Composition")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig(
    "results/composition.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 2. BATH TEMPERATURE
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    data["time_s"],
    data["temperature_C"]
)

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("BOF Bath Temperature")
plt.grid(True)

plt.tight_layout()
plt.savefig(
    "results/temperature.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 3. SCRAP MELTING
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    data["time_s"],
    data["melted_scrap_kg"]
)

plt.xlabel("Time (s)")
plt.ylabel("Melted Scrap (kg)")
plt.title("Scrap Melting")
plt.grid(True)

plt.tight_layout()
plt.savefig(
    "results/scrap_melting.png",
    dpi=300
)

plt.close()


# -------------------------------------------------
# 4. PRODUCTS
# -------------------------------------------------

plt.figure(figsize=(9, 5))

plt.plot(
    data["time_s"],
    data["CO_kg"],
    label="CO"
)

plt.plot(
    data["time_s"],
    data["slag_kg"],
    label="Simplified Slag"
)

plt.xlabel("Time (s)")
plt.ylabel("Cumulative Mass (kg)")
plt.title("Reaction Products")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig(
    "results/products.png",
    dpi=300
)

plt.close()


print("Plots generated successfully.")