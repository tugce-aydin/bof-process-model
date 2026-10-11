#include "MaterialBalance.h"

MaterialMasses calculateMaterialMasses(const ProcessState& state)
{
    MaterialMasses masses;

    masses.carbonMass =
        state.hotMetalMass * state.carbonPercent / 100.0;

    masses.siliconMass =
        state.hotMetalMass * state.siliconPercent / 100.0;

    masses.manganeseMass =
        state.hotMetalMass * state.manganesePercent / 100.0;

    masses.otherMass =
        state.hotMetalMass
        - masses.carbonMass
        - masses.siliconMass
        - masses.manganeseMass;

    return masses;
}