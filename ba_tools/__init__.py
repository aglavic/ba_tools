"""
A support package for the BornAgain software to simplify creation of models and implementation
of correct instrument resolution from instrument specific parameters.
"""

from . import patches as _patches
from .parameter_base import pp
from .simulation import ResolutionOptions, Sample, Simulation, NO_RES, FAST_RES

__version__ = "0.1"
