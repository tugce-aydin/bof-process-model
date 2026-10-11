#include "ScrapModel.h"

ScrapHeatTransfer calculateScrapHeating(
    double scrapMass,
    double scrapTemperature,
    double targetTemperature,
    double availableHeat
)
{
    const double scrapSpecificHeat = 0.75; // kJ/(kg K)

    ScrapHeatTransfer result;
    result.heatTransferred = 0.0;
    result.temperatureChange = 0.0;

    if (scrapMass <= 0.0 ||
        scrapTemperature >= targetTemperature ||
        availableHeat <= 0.0)
    {
        return result;
    }

    double heatRequired =
        scrapMass
        * scrapSpecificHeat
        * (targetTemperature - scrapTemperature);

    result.heatTransferred = availableHeat;

    if (result.heatTransferred > heatRequired)
    {
        result.heatTransferred = heatRequired;
    }

    result.temperatureChange =
        result.heatTransferred
        / (scrapMass * scrapSpecificHeat);

    return result;
}


double calculateScrapMeltingTemperature(
    double bathCarbonPercent,
    double scrapCarbonPercent
)
{
    double interfaceCarbon =
        0.8 * bathCarbonPercent
        + 0.2 * scrapCarbonPercent;

    double meltingTemperatureKelvin;

    if (interfaceCarbon <= 4.27)
    {
        meltingTemperatureKelvin =
            1810.0 - 90.0 * interfaceCarbon;
    }
    else
    {
        meltingTemperatureKelvin = 1425.0;
    }

    return meltingTemperatureKelvin - 273.15;
}


ScrapMeltingResult calculateScrapMelting(
    double solidScrapMass,
    double availableHeat
)
{
    // V1 effective latent heat of fusion
    const double latentHeat = 272.0; // kJ/kg

    ScrapMeltingResult result;
    result.meltedMass = 0.0;
    result.heatUsedForMelting = 0.0;

    if (solidScrapMass <= 0.0 ||
        availableHeat <= 0.0)
    {
        return result;
    }

    double possibleMeltedMass =
        availableHeat / latentHeat;

    result.meltedMass = possibleMeltedMass;

    if (result.meltedMass > solidScrapMass)
    {
        result.meltedMass = solidScrapMass;
    }

    result.heatUsedForMelting =
        result.meltedMass * latentHeat;

    return result;
}