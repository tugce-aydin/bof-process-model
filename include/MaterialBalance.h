#pragma once

#include "ProcessModel.h"

struct MaterialMasses
{
    double carbonMass;       // kg
    double siliconMass;      // kg
    double manganeseMass;    // kg
    double otherMass;        // kg
};

MaterialMasses calculateMaterialMasses(const ProcessState& state);