"""
Some generic instruments typical at neutron facilities.
"""
from bornagain import DistributionGate, DistributionTrapezoid, RectangularDetector, kvector_t
from numpy import arctan2, cos, sin

from ..experiment_base import Experiment
from ..units import angstrom, deg, m, mm


class GenericSANS(Experiment):
    alpha_i = 1.0 * deg
    wavelength = 6.0 * angstrom

    def __init__(
        self,
        alpha_i=0.5,
        wavelength=6.0,
        collimation_length=10000.0,
        detector_distance=10000.0,
        sample_size=20.0,
        guide_size=50.0,
        detector_size=1000.0,
        detector_pixels=200,
        dlambda_rel=0.1,
    ):
        """
        A simple SANS instrument with geometry parameters in common units.

        :param alpha_i [°]:             Incidence angle in
        :param wavelength [Å]:          Used wavelength
        :param collimation_length [m]:  Distance entrance slit/guide exit to sample
        :param detector_distance [m]:   Distance sample to detector
        :param sample_size [mm]:        Size of the (square) sample
        :param guide_size [mm]:         Size of the (square) entrance slit/guide exit
        :param detector_size [mm]:      Total size of detector (will be square)
        :param detector_pixels [pixel]: Number of pixels on the detection area
        :param dlambda_rel [1]:         Relative wavelength resolutoin (velocity selector) delta lambda/lambda
        """
        self.alpha_i = alpha_i * deg
        self.wavelength = wavelength * angstrom
        self.collimation_length = collimation_length * m
        self.detector_distance = detector_distance * m
        self.sample_size = sample_size * mm
        self.guide_size = guide_size * mm
        self.detector_size = detector_size * mm
        self.detector_pixels = detector_pixels
        self.dlambda_rel = dlambda_rel

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
        hwhm = arctan2(self.collimation_length, self.guide_size / 2.0)
        return DistributionGate(ai - hwhm, ai + hwhm)

    @property
    def res_phi(self) -> DistributionTrapezoid:
        # resolution from sample and entrance slit
        max_hw = arctan2(self.collimation_length, (self.guide_size + self.sample_size) / 2.0)
        min_hw = arctan2(self.collimation_length, (self.guide_size - self.sample_size) / 2.0)
        return DistributionTrapezoid(0.0, max_hw - min_hw, min_hw, max_hw - min_hw)
