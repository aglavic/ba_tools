"""
Some generic instruments typical at neutron facilities.
"""
from dataclasses import dataclass

from bornagain import DistributionGate, DistributionTrapezoid, RectangularDetector, kvector_t
from bornagain import millimeter as mm
from numpy import arctan2, cos, sin

from ..experiment_base import Experiment
from ..parameter_base import pp

m = mm * 1000.0


@dataclass(repr=False)
class GenericSANS(Experiment):
    alpha_i: float = pp(1.0, "deg")
    wavelength: float = pp(6.0, "angstrom")
    collimation_length: float = pp(10.0, "m")
    detector_distance: float = pp(10.0, "m")
    sample_size: float = pp(20.0, "mm")
    guide_size: float = pp(50.0, "mm")
    detector_size: float = pp(1000.0, "mm")
    detector_pixels: int = 200
    dlambda_rel: float = 0.1

    @property
    def detector(self) -> RectangularDetector:
        # Detector centered on and perpendicular to the direct beam
        det = RectangularDetector(self.detector_pixels, self.detector_size, self.detector_pixels, self.detector_size)
        dist = self.detector_distance
        if hasattr(det, "setPerpendicularToDirectBeam"):
            det.setPerpendicularToDirectBeam(dist, self.detector_size / 2.0, self.detector_size / 2.0)
        else:
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

    def _box_svg_(self):
        """
        Create a graphic configuration of the instrument in the current configuration.

        Assumes a maximum collimation length of 25m.
        """
        output = '<svg width="100%" viewBox="-250 -70 500 120" xmlns="http://www.w3.org/2000/svg">\n'

        # Guide endig at collimation length
        output += f'    <line x1="-250" y1="-10" x2="-{int(self.collimation_length/m*10)}" y2="-10" stroke="green" />\n'
        output += f'    <line x1="-250" y1="10" x2="-{int(self.collimation_length/m*10)}" y2="10" stroke="green" />\n'

        # sample
        output += '    <line x1="-10" y1="1" x2="10" y2="-1" stroke="black" />\n'

        # detector
        output += (
            f'    <line x1="{int(self.detector_distance/m*10)}" y1="-50" '
            f'x2="{int(self.detector_distance/m*10)}" y2="50" stroke="red" />\n'
        )

        output += (
            f'    <text x="-100" y="-60" text-anchor="middle" style="fill: green;">'
            f"L1={self.collimation_length/m:.1f} m</text>\n"
        )
        output += (
            f'    <text x="100" y="-60" text-anchor="middle" style="fill: red;">'
            f"L2={self.detector_distance/m:.1f} m</text>\n"
        )

        output += "</svg>"
        return output
