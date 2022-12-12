"""
A collection of patches to make code compatible with previous BA version.

Guesses the version by the existence of certain attributes.
"""

from logging import debug

import bornagain as ba

if hasattr(ba, "R3"):
    # > 1.19.0
    debug("Applyting patches for 1.19.x")
    from . import ba_1p19px
else:
    debug("Creating ParameterDistribution constants for older BornAgain version.")
    ba.ParameterDistribution.BeamWavelength = "*/Beam/Wavelength"
    ba.ParameterDistribution.BeamInclinationAngle = "*/Beam/InclinationAngle"
    ba.ParameterDistribution.BeamAzimuthalAngle = "*/Beam/AzimuthalAngle"
