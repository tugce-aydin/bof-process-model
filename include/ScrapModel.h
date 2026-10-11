#pragma once

struct ScrapHeatTransfer
{
    double heatTransferred;       // kJ
    double temperatureChange;     // Celsius
};

struct ScrapMeltingResult
{
    double meltedMass;             // kg
    double heatUsedForMelting;     // kJ
};

ScrapHeatTransfer calculateScrapHeating(
    double scrapMass,
    double scrapTemperature,
    double targetTemperature,
    double availableHeat
);

double calculateScrapMeltingTemperature(
    double bathCarbonPercent,
    double scrapCarbonPercent
);

ScrapMeltingResult calculateScrapMelting(
    double solidScrapMass,
    double availableHeat
);