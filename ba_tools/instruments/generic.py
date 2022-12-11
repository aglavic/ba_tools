"""
Some generic instruments typical at neutron facilities.
"""
from bornagain import DistributionGate, DistributionTrapezoid, RectangularDetector, kvector_t
from numpy import arctan2, cos, sin
from dataclasses import dataclass, field

from ..experiment_base import Experiment
from ..parameter_base import pp


@dataclass
class GenericSANS(Experiment):
    alpha_i:float = pp(1.0, 'deg')
    wavelength:float = pp(6.0, 'angstrom')
    collimation_length:float = pp(10.0, 'm')
    detector_distance:float = pp(10.0, 'm')
    sample_size:float = pp(20.0, 'mm')
    guide_size:float = pp(50.0, 'mm')
    detector_size:float = pp(1000.0, 'mm')
    detector_pixels:int = 200
    dlambda_rel:float = 0.1

    @property
    def detector(self) -> RectangularDetector:
        # Detector centered on and perpendicular to the direct beam
        det = RectangularDetector(self.detector_pixels, self.detector_size, self.detector_pixels, self.detector_size)
        dist = self.detector_distance
        normal = kvector_t(dist * cos(-self.alpha_i), 0.0, dist * sin(-self.alpha_i))
        det.setPosition(normal, self.detector_size / 2.0, self.detector_size / 2.0)
        return det

    @property
    def res_wavelength(self) -> DistributionTrapezoid:
        # triangular resolution of velocity selector
        fwhm = self.dlambda_rel * self.wavelength
        return DistributionTrapezoid(self.wavelength, fwhm / 2.0, 0.0, fwhm / 2.0)

    @property
    def res_alpha(self) -> DistributionGate:
        # resolution for point-like sample
        ai = self.alpha_i
        hwhm = arctan2(self.guide_size / 2.0, self.collimation_length)
        return DistributionGate(ai - hwhm, ai + hwhm)

    @property
    def res_phi(self) -> DistributionTrapezoid:
        # resolution from sample and entrance slit
        max_hw = arctan2((self.guide_size + self.sample_size) / 2.0, self.collimation_length)
        min_hw = arctan2((self.guide_size - self.sample_size) / 2.0, self.collimation_length)
        return DistributionTrapezoid(0.0, max_hw - min_hw, min_hw, max_hw - min_hw)
