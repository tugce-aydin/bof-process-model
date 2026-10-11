#pragma once

// Carbon oxidation: C + 1/2 O2 -> CO
struct CarbonReactionResult
{
    double carbonConsumed;             // kg C
    double oxygenConsumed;             // kg O2
    double carbonMonoxideProduced;     // kg CO
};

// Silicon oxidation: Si + O2 -> SiO2
struct SiliconReactionResult
{
    double siliconConsumed;             // kg Si
    double oxygenConsumed;              // kg O2
    double siliconDioxideProduced;      // kg SiO2
};

// Manganese oxidation: Mn + 1/2 O2 -> MnO
struct ManganeseReactionResult
{
    double manganeseConsumed;           // kg Mn
    double oxygenConsumed;              // kg O2
    double manganeseOxideProduced;      // kg MnO
};

struct OxygenAllocation
{
    double oxygenToCarbon;       // kg O2
    double oxygenToSilicon;      // kg O2
    double oxygenToManganese;    // kg O2
};


// Reaction calculations
CarbonReactionResult calculateCarbonOxidation(
    double carbonMass
);

SiliconReactionResult calculateSiliconOxidation(
    double siliconMass
);

ManganeseReactionResult calculateManganeseOxidation(
    double manganeseMass
);


// Oxygen flow calculations
double calculateOxygenMass(
    double oxygenFlowRate,
    double timeStepSeconds
);

double calculateCarbonFromOxygen(
    double oxygenMass
);

bool isEarlyBlowStage(
    double siliconPercent,
    double manganesePercent
);

double calculateSiliconFromOxygen(
    double oxygenMass
);

double calculateManganeseFromOxygen(
    double oxygenMass
);

OxygenAllocation calculateOxygenAllocation(
    double totalOxygenMass,
    double carbonPercent,
    double siliconPercent,
    double manganesePercent
);

double calculateLateBlowFactor(
    double carbonPercent
);

