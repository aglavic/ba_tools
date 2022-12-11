"""
Abstract base class for instrument definitions to be used to generate BornAgain simulation objects
with correct detector and resolution.

All values returned should be in BornAgain units.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, field, Field

from bornagain import IDistribution1D, RectangularDetector, millimeter as mm, nm, nm2, angstrom, deg, rad
from .parameter_base import Parametered

@dataclass
class Experiment(ABC, Parametered):
    """
    Base class for all instruments.

    Constructor should include all necessary instrument parameters.
    """

    I0: float = 1.0
    Ibg: float = 0.0

    @property
    @abstractmethod
    def alpha_i(self) -> float:
        """
        Defines angle of incidence to sample.
        """

    @property
    @abstractmethod
    def wavelength(self) -> float:
        """
        Defines incidence wavelength.
        """

    @property
    @abstractmethod
    def detector(self) -> RectangularDetector:
        """
        Defines center of the detector in horizontal direction.
        """

    @property
    @abstractmethod
    def res_wavelength(self) -> IDistribution1D:
        """
        Wavelength resolution.
        """

    @property
    @abstractmethod
    def res_alpha(self) -> IDistribution1D:
        """
        Horizontal beam resolution.
        """

    @property
    @abstractmethod
    def res_phi(self) -> IDistribution1D:
        """
        Vertical beam resolution.
        """
