#include <fstream>
#include <iostream>
#include <random>
#include "ProcessModel.h"

void generateDataset(
    int numberOfSamples,
    const std::string& datasetFile
)
{
    std::ofstream file(datasetFile);

    if (!file.is_open())
    {
        std::cerr << "Dataset file could not be created." << std::endl;
        return;
    }

    file
        << "hot_metal_kg,"
        << "scrap_kg,"
        << "initial_temp_C,"
        << "initial_C_pct,"
        << "initial_Si_pct,"
        << "initial_Mn_pct,"
        << "oxygen_flow_Nm3_min,"
        << "target_C_pct,"
        << "endpoint_reached,"
        << "endpoint_time_s,"
        << "endpoint_temp_C\n";

    std::mt19937 generator(42);

    std::uniform_real_distribution<double> hotMetalDist(90000.0, 110000.0);
    std::uniform_real_distribution<double> scrapDist(10000.0, 20000.0);
    std::uniform_real_distribution<double> temperatureDist(1300.0, 1400.0);

    std::uniform_real_distribution<double> carbonDist(4.0, 5.0);
    std::uniform_real_distribution<double> siliconDist(0.3, 0.7);
    std::uniform_real_distribution<double> manganeseDist(0.2, 0.6);

    std::uniform_real_distribution<double> oxygenDist(250.0, 350.0);

    for (int i = 0; i < numberOfSamples; ++i)
    {
        ProcessInput input;

        input.hotMetalMass = hotMetalDist(generator);
        input.scrapMass = scrapDist(generator);
        input.initialTemperature = temperatureDist(generator);

        input.initialCarbonPercent = carbonDist(generator);
        input.initialSiliconPercent = siliconDist(generator);
        input.initialManganesePercent = manganeseDist(generator);

        input.oxygenFlowRate = oxygenDist(generator);

        input.scrapInitialTemperature = 25.0;
        input.targetCarbonPercent = 0.06;

        std::string simulationFile =
            "../results/ml_temp_" + std::to_string(i) + ".csv";

        ProcessResult result = runSimulation(
            input,
            1500.0,
            1.0,
            simulationFile
        );

        file
            << input.hotMetalMass << ","
            << input.scrapMass << ","
            << input.initialTemperature << ","
            << input.initialCarbonPercent << ","
            << input.initialSiliconPercent << ","
            << input.initialManganesePercent << ","
            << input.oxygenFlowRate << ","
            << input.targetCarbonPercent << ","
            << (result.endpointReached ? 1 : 0) << ","
            << result.endpointTime << ","
            << result.endpointTemperature
            << "\n";

        std::cout
            << "Dataset sample "
            << i + 1
            << "/"
            << numberOfSamples
            << " completed."
            << std::endl;
    }

    file.close();

    std::cout
        << "\nDataset saved to: "
        << datasetFile
        << std::endl;
}