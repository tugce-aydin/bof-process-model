#include "ReactionModel.h"

CarbonReactionResult calculateCarbonOxidation(double carbonMass)
{
    CarbonReactionResult result;

    result.carbonConsumed = carbonMass;

    result.oxygenConsumed =
        carbonMass * (16.0 / 12.0);

    result.carbonMonoxideProduced =
        carbonMass * (28.0 / 12.0);

    return result;
}


double calculateOxygenMass(
    double oxygenFlowRate,
    double timeStepSeconds
)
{
    const double oxygenDensity = 1.429; // kg/Nm^3

    double oxygenVolume =
        oxygenFlowRate * (timeStepSeconds / 60.0);

    double oxygenMass =
        oxygenVolume * oxygenDensity;

    return oxygenMass;
}


double calculateCarbonFromOxygen(
    double oxygenMass
)
{
    double carbonMass =
        oxygenMass * (12.0 / 16.0);

    return carbonMass;
}


SiliconReactionResult calculateSiliconOxidation(
    double siliconMass
)
{
    SiliconReactionResult result;

    result.siliconConsumed = siliconMass;

    result.oxygenConsumed =
        siliconMass * (32.0 / 28.0);

    result.siliconDioxideProduced =
        siliconMass * (60.0 / 28.0);

    return result;
}


ManganeseReactionResult calculateManganeseOxidation(
    double manganeseMass
)
{
    ManganeseReactionResult result;

    result.manganeseConsumed = manganeseMass;

    result.oxygenConsumed =
        manganeseMass * (16.0 / 55.0);

    result.manganeseOxideProduced =
        manganeseMass * (71.0 / 55.0);

    return result;
}


bool isEarlyBlowStage(
    double siliconPercent,
    double manganesePercent
)
{
    double influenceIndex =
        siliconPercent
        + 0.25 * manganesePercent;

    return influenceIndex >= 0.1;
}


double calculateSiliconFromOxygen(
    double oxygenMass
)
{
    double siliconMass =
        oxygenMass * (28.0 / 32.0);

    return siliconMass;
}


double calculateManganeseFromOxygen(
    double oxygenMass
)
{
    double manganeseMass =
        oxygenMass * (55.0 / 16.0);

    return manganeseMass;
}


OxygenAllocation calculateOxygenAllocation(
    double totalOxygenMass,
    double carbonPercent,
    double siliconPercent,
    double manganesePercent
)
{
    const double siliconWeightFactor = 10.0;
    const double manganeseWeightFactor = 5.0;

    double carbonWeight =
        carbonPercent;

    double siliconWeight =
        siliconWeightFactor * siliconPercent;

    double manganeseWeight =
        manganeseWeightFactor * manganesePercent;

    double totalWeight =
        carbonWeight
        + siliconWeight
        + manganeseWeight;

    // Start with zero oxygen allocation.
    OxygenAllocation allocation{
        0.0,
        0.0,
        0.0
    };

    // Numerical protection:
    // if no reactive C, Si or Mn remains,
    // oxygen is not allocated to these reactions.
    if (totalWeight <= 1e-12)
    {
        return allocation;
    }

    allocation.oxygenToCarbon =
        totalOxygenMass
        * carbonWeight
        / totalWeight;

    allocation.oxygenToSilicon =
        totalOxygenMass
        * siliconWeight
        / totalWeight;

    allocation.oxygenToManganese =
        totalOxygenMass
        * manganeseWeight
        / totalWeight;

    return allocation;
}

double calculateLateBlowFactor(
    double carbonPercent
)
{
    const double criticalCarbonPercent = 0.36;

    if (carbonPercent >= criticalCarbonPercent)
    {
        return 1.0;
    }

    if (carbonPercent <= 0.0)
    {
        return 0.0;
    }

    return carbonPercent / criticalCarbonPercent;
}