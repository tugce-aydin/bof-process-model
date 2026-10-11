#pragma once

#include <fstream>
#include <string>

class SimulationLogger
{
private:
    std::ofstream file;

public:
    SimulationLogger(const std::string& filePath);

    void writeHeader();

    void writeRow(
        double time,
        double carbonPercent,
        double siliconPercent,
        double manganesePercent,
        double temperature,
        double meltedScrap,
        double carbonMonoxide,
        double slag
    );
};