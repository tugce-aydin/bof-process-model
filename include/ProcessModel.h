#pragma once

#include <string>

struct ProcessInput
{
    double hotMetalMass;
    double scrapMass;
    double initialTemperature;

    double initialCarbonPercent;
    double initialSiliconPercent;
    double initialManganesePercent;

    double oxygenFlowRate;
    double scrapInitialTemperature;
    double targetCarbonPercent;
};

struct ProcessState
{
    double hotMetalMass;
    double scrapMass;
    double temperature;

    double carbonPercent;
    double siliconPercent;
    double manganesePercent;

    double oxygenFlowRate;
    double time;

    double scrapTemperature;
    double meltedScrapMass;
};

struct ProcessResult
{
    bool endpointReached;

    double endpointTime;
    double endpointTemperature;
    double endpointCarbonPercent;

    double finalSiliconPercent;
    double finalManganesePercent;

    double meltedScrapMass;

    double totalCOProduced;
    double totalSlagProduced;

    double totalOxygenSupplied;
    double totalOxygenConsumed;
};

ProcessResult runSimulation(
    ProcessState& state,
    double simulationTime,
    double timeStep,
    const std::string& outputFile,
    double targetCarbonPercent
);

ProcessResult runSimulation(
    const ProcessInput& input,
    double simulationTime,
    double timeStep,
    const std::string& outputFile
);