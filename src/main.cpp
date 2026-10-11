#include <iostream>
#include <string>
#include <cstdlib>

#include "DatasetGenerator.h"
#include "ProcessModel.h"


void printUsage()
{
    std::cout
        << "BOF Dynamic Process Model\n\n"
        << "Usage:\n"
        << "  ./bof_model --dataset <number_of_samples>\n\n"
        << "  ./bof_model --simulate "
        << "<hot_metal_kg> "
        << "<scrap_kg> "
        << "<initial_temp_C> "
        << "<initial_C_pct> "
        << "<initial_Si_pct> "
        << "<initial_Mn_pct> "
        << "<oxygen_flow_Nm3_min> "
        << "<target_C_pct> "
        << "<output_csv>\n";

    std::cout << std::endl;
}


int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        printUsage();
        return 1;
    }

    std::string mode = argv[1];

    // Dataset generation mode
    if (mode == "--dataset")
    {
        if (argc != 3)
        {
            std::cerr
                << "Usage: ./bof_model --dataset "
                << "<number_of_samples>"
                << std::endl;

            return 1;
        }

        int numberOfSamples = std::stoi(argv[2]);

        std::cout
            << "Generating "
            << numberOfSamples
            << " ML dataset samples..."
            << std::endl;

        generateDataset(
            numberOfSamples,
            "../data/ml_dataset.csv"
        );

        return 0;
    }

    // Single simulation mode
    if (mode == "--simulate")
    {
        if (argc != 11)
        {
            std::cerr
                << "Invalid simulation arguments."
                << std::endl;

            printUsage();
            return 1;
        }

        ProcessInput input;

        input.hotMetalMass =
            std::stod(argv[2]);

        input.scrapMass =
            std::stod(argv[3]);

        input.initialTemperature =
            std::stod(argv[4]);

        input.initialCarbonPercent =
            std::stod(argv[5]);

        input.initialSiliconPercent =
            std::stod(argv[6]);

        input.initialManganesePercent =
            std::stod(argv[7]);

        input.oxygenFlowRate =
            std::stod(argv[8]);

        input.targetCarbonPercent =
            std::stod(argv[9]);

        input.scrapInitialTemperature = 25.0;

        std::string outputFile = argv[10];

        ProcessResult result = runSimulation(
            input,
            1500.0,
            1.0,
            outputFile
        );

        // Machine-readable result for the GUI
        std::cout
            << "\nGUI_RESULT,"
            << (result.endpointReached ? 1 : 0)
            << ","
            << result.endpointTime
            << ","
            << result.endpointTemperature
            << ","
            << result.endpointCarbonPercent
            << ","
            << result.finalSiliconPercent
            << ","
            << result.finalManganesePercent
            << ","
            << result.meltedScrapMass
            << ","
            << result.totalCOProduced
            << ","
            << result.totalSlagProduced
            << std::endl;

        return 0;
    }

    std::cerr
        << "Unknown mode: "
        << mode
        << std::endl;

    printUsage();

    return 1;
}