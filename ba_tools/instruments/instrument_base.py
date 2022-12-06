"""
Abstract base class for instrument definitions to be used to generate BornAgain simulation objects
with correct detector and resolution.

All values returned should be in BornAgain units.
"""

from abc import ABC, abstractmethod

from bornagain import IDistribution1D, RectangularDetector


class Instrument(ABC):
    """
    Base class for all instruments.

    Constructor should include all necessary instrument parameters.
    """

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
