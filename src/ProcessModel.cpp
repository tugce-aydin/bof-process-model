#include <iostream>
#include "ProcessModel.h"
#include "MaterialBalance.h"
#include "ReactionModel.h"
#include "EnergyBalance.h"
#include "ScrapModel.h"
#include "SimulationLogger.h"
#include <string>

ProcessResult runSimulation(
    ProcessState& state,
    double simulationTime,
    double timeStep,
    const std::string& outputFile,
    double targetCarbonPercent
)

{
    MaterialMasses masses =
        calculateMaterialMasses(state);
    double currentMetalMass =
        state.hotMetalMass;
    const double scrapCarbonPercent = 0.08;
    const double ambientTemperature = 25.0;
    
    const double gasOutletTemperature = 900.0; // C, assumed
    const double gasSpecificHeat = 1.10; // kJ/(kg K), assumed
    const double slagSpecificHeat = 1.00; // kJ/(kg K), assumed
    const double initialHotMetalMass =
        state.hotMetalMass;
    const double initialScrapMass =
        state.scrapMass;
    double totalReactionHeat = 0.0;
    double totalScrapHeating = 0.0;
    double totalScrapMelting = 0.0;
    double totalHeatLoss = 0.0;
    double totalGasSensibleHeat = 0.0;
    double totalSlagSensibleHeat = 0.0;
    double totalBathEnergy = 0.0;
    double totalCOProduced = 0.0;
    double totalSiO2Produced = 0.0;
    double totalMnOProduced = 0.0;
    double totalOxygenSupplied = 0.0;
    double totalOxygenConsumed = 0.0;
    SimulationLogger logger(
        outputFile
    );
    logger.writeHeader();
    logger.writeRow(
        state.time,
        state.carbonPercent,
        state.siliconPercent,
        state.manganesePercent,
        state.temperature,
        state.meltedScrapMass,
        0.0,
        0.0
    );
    std::cout << std::endl;
    std::cout
        << "=== MULTI-REACTION TIME SIMULATION ==="
        << std::endl;
    bool endpointReached = state.carbonPercent <= targetCarbonPercent;
    while (state.time < simulationTime && !endpointReached)
    {
        double oxygenMass =
            calculateOxygenMass(
                state.oxygenFlowRate,
                timeStep
            );
        totalOxygenSupplied +=
            oxygenMass;
        OxygenAllocation allocation =
            calculateOxygenAllocation(
                oxygenMass,
                state.carbonPercent,
                state.siliconPercent,
                state.manganesePercent
            );
        double carbonRemoved =
            calculateCarbonFromOxygen(
                allocation.oxygenToCarbon
            );
    // Empirical low-carbon correction; not plant-calibrated.
    const double criticalCarbonPercent = 0.36;
    if (state.carbonPercent < criticalCarbonPercent)
    {
        double factor = state.carbonPercent / criticalCarbonPercent;
        if (factor < 0.0) factor = 0.0;
        carbonRemoved *= factor;
    }
    double siliconRemoved =
            calculateSiliconFromOxygen(
                allocation.oxygenToSilicon
            );
        double manganeseRemoved =
            calculateManganeseFromOxygen(
                allocation.oxygenToManganese
            );
        if (carbonRemoved > masses.carbonMass)
        {
            carbonRemoved = masses.carbonMass;
        }
        if (siliconRemoved > masses.siliconMass)
        {
            siliconRemoved = masses.siliconMass;
        }
        if (manganeseRemoved > masses.manganeseMass)
        {
            manganeseRemoved = masses.manganeseMass;
        }
        CarbonReactionResult carbonReaction =
            calculateCarbonOxidation(
                carbonRemoved
            );
        SiliconReactionResult siliconReaction =
            calculateSiliconOxidation(
                siliconRemoved
            );
        ManganeseReactionResult manganeseReaction =
            calculateManganeseOxidation(
                manganeseRemoved
            );
        totalCOProduced +=
            carbonReaction.carbonMonoxideProduced;
        totalSiO2Produced +=
            siliconReaction.siliconDioxideProduced;
        totalMnOProduced +=
            manganeseReaction.manganeseOxideProduced;
        double oxygenConsumedThisStep =
            carbonReaction.oxygenConsumed
            + siliconReaction.oxygenConsumed
            + manganeseReaction.oxygenConsumed;
        totalOxygenConsumed +=
            oxygenConsumedThisStep;
        ReactionHeat reactionHeat =
            calculateReactionHeat(
                carbonRemoved,
                siliconRemoved,
                manganeseRemoved
            );
    totalReactionHeat +=
        reactionHeat.totalHeat;
    // Sensible heat carried away by the generated gas and slag.
    double gasHeatThisStep =
        carbonReaction.carbonMonoxideProduced
        * gasSpecificHeat
        * (gasOutletTemperature - ambientTemperature);
    double slagHeatThisStep =
        (siliconReaction.siliconDioxideProduced + manganeseReaction.manganeseOxideProduced)
        * slagSpecificHeat
        * (state.temperature - ambientTemperature);
    totalGasSensibleHeat += gasHeatThisStep;
    totalSlagSensibleHeat += slagHeatThisStep;
        masses.carbonMass -=
            carbonRemoved;
        masses.siliconMass -=
            siliconRemoved;
        masses.manganeseMass -=
            manganeseRemoved;
        currentMetalMass -=
            carbonRemoved
            + siliconRemoved
            + manganeseRemoved;
        double solidScrapMass =
            state.scrapMass
            - state.meltedScrapMass;
        double scrapMeltingTemperature =
            calculateScrapMeltingTemperature(
                state.carbonPercent,
                scrapCarbonPercent
            );
        ScrapHeatTransfer scrapHeating =
            calculateScrapHeating(
                solidScrapMass,
                state.scrapTemperature,
                scrapMeltingTemperature,
                (reactionHeat.totalHeat > gasHeatThisStep + slagHeatThisStep)
                    ? reactionHeat.totalHeat - gasHeatThisStep - slagHeatThisStep
                    : 0.0
            );
        state.scrapTemperature +=
            scrapHeating.temperatureChange;
        totalScrapHeating +=
            scrapHeating.heatTransferred;
        double heatRemaining =
            reactionHeat.totalHeat
            - gasHeatThisStep
            - slagHeatThisStep
            - scrapHeating.heatTransferred;
        if (
            state.scrapTemperature >=
                scrapMeltingTemperature
            &&
            solidScrapMass > 0.0
        )
        {
            ScrapMeltingResult melting =
                calculateScrapMelting(
                    solidScrapMass,
                    heatRemaining
                );
            double carbonFromScrap =
                melting.meltedMass
                * scrapCarbonPercent
                / 100.0;
            double otherFromScrap =
                melting.meltedMass
                - carbonFromScrap;
            state.meltedScrapMass +=
                melting.meltedMass;
            masses.carbonMass +=
                carbonFromScrap;
            masses.otherMass +=
                otherFromScrap;
            currentMetalMass +=
                melting.meltedMass;
            heatRemaining -=
                melting.heatUsedForMelting;
            totalScrapMelting +=
                melting.heatUsedForMelting;
        }
        double heatLoss =
            calculateHeatLoss(
                state.temperature,
                ambientTemperature,
                timeStep
            );
        heatRemaining -=
            heatLoss;
        totalHeatLoss +=
            heatLoss;
        totalBathEnergy +=
            heatRemaining;
        double temperatureChange =
            calculateTemperatureChange(
                heatRemaining,
                currentMetalMass
            );
        state.temperature +=
            temperatureChange;
        state.carbonPercent =
            masses.carbonMass
            / currentMetalMass
            * 100.0;
        state.siliconPercent =
            masses.siliconMass
            / currentMetalMass
            * 100.0;
        state.manganesePercent =
            masses.manganeseMass
            / currentMetalMass
            * 100.0;
        state.time +=
            timeStep;
        endpointReached = state.carbonPercent <= targetCarbonPercent;
        double currentSlagMass =
            totalSiO2Produced
            + totalMnOProduced;
        logger.writeRow(
            state.time,
            state.carbonPercent,
            state.siliconPercent,
            state.manganesePercent,
            state.temperature,
            state.meltedScrapMass,
            totalCOProduced,
            currentSlagMass
        );
        std::cout
            << "t = "
            << state.time
            << " s"
            << " | C = "
            << state.carbonPercent
            << " wt.%"
            << " | Si = "
            << state.siliconPercent
            << " wt.%"
            << " | Mn = "
            << state.manganesePercent
            << " wt.%"
            << " | T = "
            << state.temperature
            << " C"
            << " | Scrap T = "
            << state.scrapTemperature
            << " C"
            << " | Melted Scrap = "
            << state.meltedScrapMass
            << " kg"
            << std::endl;
    }
    double totalEnergyUsed =
        totalScrapHeating
        + totalScrapMelting
        + totalHeatLoss
        + totalGasSensibleHeat
        + totalSlagSensibleHeat
        + totalBathEnergy;
    double energyBalanceError = 0.0;
    if (totalReactionHeat != 0.0)
    {
        energyBalanceError =
            (
                totalReactionHeat
                - totalEnergyUsed
            )
            / totalReactionHeat
            * 100.0;
    }
    std::cout << std::endl;
    std::cout
        << "=== ENERGY BALANCE SUMMARY ==="
        << std::endl;
    std::cout
        << "Reaction heat: "
        << totalReactionHeat
        << " kJ"
        << std::endl;
    std::cout
        << "Scrap heating: "
        << totalScrapHeating
        << " kJ"
        << std::endl;
    std::cout
        << "Scrap melting: "
        << totalScrapMelting
        << " kJ"
        << std::endl;
    std::cout
        << "Heat loss: "
        << totalHeatLoss
        << " kJ"
        << std::endl;
    std::cout << "Gas sensible heat: " << totalGasSensibleHeat << " kJ" << std::endl;
    std::cout << "Slag sensible heat: " << totalSlagSensibleHeat << " kJ" << std::endl;
    std::cout
        << "Bath net energy: "
        << totalBathEnergy
        << " kJ"
        << std::endl;
    std::cout
        << "Energy balance error: "
        << energyBalanceError
        << " %"
        << std::endl;
    double totalSlagProduced =
        totalSiO2Produced
        + totalMnOProduced;
    std::cout << std::endl;
    std::cout
        << "=== GAS AND SLAG SUMMARY ==="
        << std::endl;
    std::cout
        << "CO produced: "
        << totalCOProduced
        << " kg"
        << std::endl;
    std::cout
        << "SiO2 produced: "
        << totalSiO2Produced
        << " kg"
        << std::endl;
    std::cout
        << "MnO produced: "
        << totalMnOProduced
        << " kg"
        << std::endl;
    std::cout
        << "Total simplified slag: "
        << totalSlagProduced
        << " kg"
        << std::endl;
    double unusedOxygen =
        totalOxygenSupplied
        - totalOxygenConsumed;
    std::cout << std::endl;
    std::cout
        << "=== OXYGEN SUMMARY ==="
        << std::endl;
    std::cout
        << "Oxygen supplied: "
        << totalOxygenSupplied
        << " kg"
        << std::endl;
    std::cout
        << "Oxygen consumed: "
        << totalOxygenConsumed
        << " kg"
        << std::endl;
    std::cout
        << "Unused oxygen: "
        << unusedOxygen
        << " kg"
        << std::endl;
    double finalSolidScrap =
        state.scrapMass
        - state.meltedScrapMass;
    double totalMassInput =
        initialHotMetalMass
        + initialScrapMass
        + totalOxygenSupplied;
    double totalMassOutput =
        currentMetalMass
        + finalSolidScrap
        + totalCOProduced
        + totalSlagProduced
        + unusedOxygen;
    double massBalanceResidual =
        totalMassInput
        - totalMassOutput;
    double massBalanceError = 0.0;
    if (totalMassInput != 0.0)
    {
        massBalanceError =
            massBalanceResidual
            / totalMassInput
            * 100.0;
    }
    std::cout << std::endl;
    std::cout
        << "=== MASS BALANCE SUMMARY ==="
        << std::endl;
    std::cout
        << "Total mass input: "
        << totalMassInput
        << " kg"
        << std::endl;
    std::cout
        << "Liquid metal: "
        << currentMetalMass
        << " kg"
        << std::endl;
    std::cout
        << "Solid scrap remaining: "
        << finalSolidScrap
        << " kg"
        << std::endl;
    std::cout
        << "Gas mass: "
        << totalCOProduced
        << " kg"
        << std::endl;
    std::cout
        << "Simplified slag mass: "
        << totalSlagProduced
        << " kg"
        << std::endl;
    std::cout
        << "Unused oxygen: "
        << unusedOxygen
        << " kg"
        << std::endl;
    std::cout
        << "Mass balance residual: "
        << massBalanceResidual
        << " kg"
        << std::endl;
    std::cout
        << "Mass balance error: "
        << massBalanceError
        << " %"
        << std::endl;
    std::cout << std::endl;
    std::cout << "\n=== ENDPOINT SUMMARY ===\n";
    std::cout << "Target carbon: " << targetCarbonPercent << " wt.%\n";
    std::cout << "Endpoint reached: " << (endpointReached ? "yes" : "no") << "\n";
    std::cout << "End time: " << state.time << " s\n";
    std::cout << "End carbon: " << state.carbonPercent << " wt.%\n";
    std::cout << "End temperature: " << state.temperature << " C\n";
    std::cout << "Temperature is an uncalibrated estimate, not an industrial prediction.\n";
    std::cout
    << "Simulation data saved to: "
    << outputFile
    << std::endl;

ProcessResult result;

result.endpointReached = endpointReached;

result.endpointTime = state.time;
result.endpointTemperature = state.temperature;
result.endpointCarbonPercent = state.carbonPercent;

result.finalSiliconPercent = state.siliconPercent;
result.finalManganesePercent = state.manganesePercent;

result.meltedScrapMass = state.meltedScrapMass;

result.totalCOProduced = totalCOProduced;
result.totalSlagProduced = totalSlagProduced;

result.totalOxygenSupplied = totalOxygenSupplied;
result.totalOxygenConsumed = totalOxygenConsumed;

return result;
}


ProcessResult runSimulation(
    const ProcessInput& input,
    double simulationTime,
    double timeStep,
    const std::string& outputFile
)
{
    ProcessState state;

    state.hotMetalMass = input.hotMetalMass;
    state.scrapMass = input.scrapMass;
    state.temperature = input.initialTemperature;

    state.carbonPercent = input.initialCarbonPercent;
    state.siliconPercent = input.initialSiliconPercent;
    state.manganesePercent = input.initialManganesePercent;

    state.oxygenFlowRate = input.oxygenFlowRate;
    state.time = 0.0;

    state.scrapTemperature = input.scrapInitialTemperature;
    state.meltedScrapMass = 0.0;

    return runSimulation(
        state,
        simulationTime,
        timeStep,
        outputFile,
        input.targetCarbonPercent
    );
}

