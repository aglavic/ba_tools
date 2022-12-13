"""
Abstract base class for instrument definitions to be used to generate BornAgain simulation objects
with correct detector and resolution.

All values returned should be in BornAgain units.
"""

from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, field, fields

from bornagain import IDistribution1D, RectangularDetector, angstrom, deg
from bornagain import millimeter as mm
from bornagain import nm, nm2, rad

from .parameter_base import Parametered


@dataclass(repr=False)
class Experiment(ABC, Parametered):
    """
    Base class for all instruments.

    Constructor should include all necessary instrument parameters.
    """

    I0: float = 1.0
    Ibg: float = 0.0

    class Config(Parametered):
        """
        All configuration parameters for the instument that can be considered "fixed".
        This helps to separate user configurable options from hardware/alignment given ones.

        An example would be the center of the direct beam on the detector,
        that will not change during the course of an experiment.
        """

        ...

    _config = Config()

    @classmethod
    def set_config(cls, config: Config = None, **kwargs):
        """
        Define general instrument configuration parameters. The
        parameters are defined in the object.Config class (if it exists)
        and can be provided either as an instance of that class or
        as keyword parameters when calling set_config.
        Any missing arguments are set to default.

        For the possible keywords see object.Config.
        """
        if config is None:
            config = cls.Config(**kwargs)
        if not isinstance(config, cls.Config):
            raise TypeError(f"Only {cls.Config.__qualname__} objects can be sued as configuration.")
        cls._config = config

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

    def apply_fast_resolution(self, data, wavelengt=False, alpha=True, phi=True):
        """
        A fast implementation of resolution that works directly on a simulated
        image. Will not include changes in scattering from incident beam resolution.
        """
        raise NotImplemented(f'Class {self.__class__.__qualname__} does not define fast resolution convolution')