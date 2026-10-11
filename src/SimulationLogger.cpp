#include "SimulationLogger.h"


SimulationLogger::SimulationLogger(
    const std::string& filePath
)
{
    file.open(filePath);
}


void SimulationLogger::writeHeader()
{
    file
        << "time_s,"
        << "carbon_wt_pct,"
        << "silicon_wt_pct,"
        << "manganese_wt_pct,"
        << "temperature_C,"
        << "melted_scrap_kg,"
        << "CO_kg,"
        << "slag_kg"
        << "\n";
}


void SimulationLogger::writeRow(
    double time,
    double carbonPercent,
    double siliconPercent,
    double manganesePercent,
    double temperature,
    double meltedScrap,
    double carbonMonoxide,
    double slag
)
{
    file
        << time << ","
        << carbonPercent << ","
        << siliconPercent << ","
        << manganesePercent << ","
        << temperature << ","
        << meltedScrap << ","
        << carbonMonoxide << ","
        << slag
        << "\n";
}

