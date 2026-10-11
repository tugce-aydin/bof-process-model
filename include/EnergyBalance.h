#pragma once

struct ReactionHeat
{
    double carbonHeat;
    double siliconHeat;
    double manganeseHeat;
    double totalHeat;
};

ReactionHeat calculateReactionHeat(
    double carbonRemoved,
    double siliconRemoved,
    double manganeseRemoved
);

double calculateTemperatureChange(
    double totalHeat,
    double metalMass
);

double calculateHeatLoss(
    double bathTemperature,
    double ambientTemperature,
    double timeStep
);

