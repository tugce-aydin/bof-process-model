#include "EnergyBalance.h"

ReactionHeat calculateReactionHeat(
    double carbonRemoved,
    double siliconRemoved,
    double manganeseRemoved
)
{
    const double carbonEnthalpy = 118.613;
    const double siliconEnthalpy = 945.172;
    const double manganeseEnthalpy = 384.9;

    const double carbonMolarMass = 12.0;
    const double siliconMolarMass = 28.0;
    const double manganeseMolarMass = 55.0;

    ReactionHeat heat;

    heat.carbonHeat =
        (carbonRemoved / carbonMolarMass)
        * carbonEnthalpy
        * 1000.0;

    heat.siliconHeat =
        (siliconRemoved / siliconMolarMass)
        * siliconEnthalpy
        * 1000.0;

    heat.manganeseHeat =
        (manganeseRemoved / manganeseMolarMass)
        * manganeseEnthalpy
        * 1000.0;

    heat.totalHeat =
        heat.carbonHeat
        + heat.siliconHeat
        + heat.manganeseHeat;

    return heat;
}

double calculateTemperatureChange(
    double totalHeat,
    double metalMass
)
{
    const double specificHeatCapacity = 0.820;

    if (metalMass <= 0.0)
    {
        return 0.0;
    }

    double temperatureChange =
        totalHeat
        / (metalMass * specificHeatCapacity);

    return temperatureChange;
}

double calculateHeatLoss(
    double bathTemperature,
    double ambientTemperature,
    double timeStep
)
{
    // V1 effective heat-loss coefficient
    const double heatLossCoefficient = 5.0; // kJ/(s K)

    if (bathTemperature <= ambientTemperature)
    {
        return 0.0;
    }

    return heatLossCoefficient
        * (bathTemperature - ambientTemperature)
        * timeStep;
}

