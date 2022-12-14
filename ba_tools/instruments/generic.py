"""
Some generic instruments typical at neutron facilities.
"""
from dataclasses import dataclass

from bornagain import DistributionGate, DistributionTrapezoid, RectangularDetector, kvector_t
from bornagain import millimeter as mm
from numpy import arange, arctan2, cos, empty, linspace, maximum, meshgrid, newaxis, ones, sin, sqrt, where, zeros_like

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

    @dataclass(repr=False)
    class Config(Experiment.Config):
        guide_size: float = pp(50.0, "mm")
        detector_size: float = pp(1000.0, "mm")
        detector_pixels: int = 200
        center_x_pix: float = 100.0
        center_y_pix: float = 100.0
        dlambda_rel: float = 0.1

    _config = Config()

    @property
    def detector(self) -> RectangularDetector:
        # Detector centered on and perpendicular to the direct beam
        det = RectangularDetector(
            self._config.detector_pixels,
            self._config.detector_size,
            self._config.detector_pixels,
            self._config.detector_size,
        )
        dist = self.detector_distance
        x0 = self._config.detector_size * self._config.center_x_pix / self._config.detector_pixels
        y0 = self._config.detector_size * self._config.center_y_pix / self._config.detector_pixels
        if hasattr(det, "setPerpendicularToDirectBeam"):
            det.setPerpendicularToDirectBeam(dist, x0, y0)
        else:
            normal = kvector_t(dist * cos(-self.alpha_i), 0.0, dist * sin(-self.alpha_i))
            det.setPosition(normal, x0, y0)
        return det

    @property
    def res_wavelength(self) -> DistributionTrapezoid:
        # triangular resolution of velocity selector
        fwhm = self._config.dlambda_rel * self.wavelength
        return DistributionTrapezoid(self.wavelength, fwhm, 0.0, fwhm)

    @property
    def res_alpha(self) -> DistributionGate:
        # resolution for point-like sample
        hwhm = arctan2(self._config.guide_size / 2.0, self.collimation_length)
        return DistributionGate(self.alpha_i - hwhm, self.alpha_i + hwhm)

    @property
    def res_phi(self) -> DistributionTrapezoid:
        # resolution from sample and entrance slit
        max_hw = arctan2((self._config.guide_size + self.sample_size) / 2.0, self.collimation_length)
        min_hw = arctan2((self._config.guide_size - self.sample_size) / 2.0, self.collimation_length)
        return DistributionTrapezoid(0.0, max_hw - min_hw, 2 * min_hw, max_hw - min_hw)

    def apply_fast_resolution(self, data, wavelengt=False, alpha=True, phi=True):
        """
        Implements effect of resolution with fast convolution.

        Angular resolution is done using FFT convolution,
        wavelength spread is later added with second
        convolution that includes the effect of relative spread.
        """

        if wavelengt:
            xy = arange(self._config.detector_pixels)
            # pixel distanc from beam center
            R = sqrt(
                ((xy - self._config.center_x_pix) ** 2)[:, newaxis]
                + ((xy - self._config.center_y_pix) ** 2)[newaxis, :]
            )
            Phi = arctan2((xy - self._config.center_x_pix)[:, newaxis], (xy - self._config.center_y_pix)[newaxis, :])
            res_max = self._config.dlambda_rel  # FWHM of triangular distribution
            result_a = zeros_like(data)
            for i in xy:
                for j in xy:
                    Rij = R[j, i]
                    Phiij = Phi[j, i]
                    res_pts = Rij * res_max  # need to cover FWHM range around the center point
                    N = 0.0
                    i_range = int(2 * res_pts * abs(cos(Phiij)))
                    j_range = int(2 * res_pts * abs(sin(Phiij)))
                    if (
                        (i - i_range) < 0
                        or (j - j_range) < 0
                        or (i + i_range) >= xy[-1]
                        or (j + j_range) >= xy[-1]
                        or max(i_range, j_range) < 2
                    ):
                        result_a[i, j] = data[i, j]
                        continue

                    if i_range > j_range:
                        ij_scale = j_range / i_range
                        for k in range(-i_range // 2, i_range // 2 + 1):
                            f = 0.5 - abs(k) / i_range
                            N += f
                            result_a[i, j] += f * data[i + k, j + int(k * ij_scale)]
                    else:
                        ij_scale = i_range / j_range
                        for k in range(-j_range // 2, j_range // 2 + 1):
                            f = 0.5 - abs(k) / j_range
                            N += f
                            result_a[i, j] += f * data[i + int(k * ij_scale), j + k]
                    result_a[i, j] /= N
            data = result_a

        if alpha and phi:
            from scipy.signal import fftconvolve

            # implement angular resolution, vertical directly defined by size of kernel
            angle_per_pixel = arctan2(self._config.detector_size / self._config.detector_pixels, self.detector_distance)
            alpha_res = arctan2(self._config.guide_size / 2.0, self.collimation_length)
            kernel_height = int(2 * alpha_res / angle_per_pixel) + 1
            max_hw = arctan2((self._config.guide_size + self.sample_size) / 2.0, self.collimation_length)
            min_hw = arctan2((self._config.guide_size - self.sample_size) / 2.0, self.collimation_length)
            kernel_width = int(2 * max_hw / angle_per_pixel) + 1
            dx = linspace(-kernel_width / 2.0, kernel_width / 2.0, kernel_width)
            kernel = (
                ones(kernel_height)[:, newaxis]
                * where(
                    abs(dx) < (min_hw / angle_per_pixel),
                    1.0,
                    maximum(1.0 - (abs(dx) - min_hw / angle_per_pixel) / (max_hw - min_hw) * angle_per_pixel, 0.0),
                )[newaxis, :]
            )
            norm = kernel.sum()
            if norm == 0.0:
                return data
            kernel /= norm
            data = fftconvolve(data, kernel, mode="same")
        elif phi:
            from scipy.signal import fftconvolve

            # implement angular resolution, vertical directly defined by size of kernel
            angle_per_pixel = arctan2(self._config.detector_size / self._config.detector_pixels, self.detector_distance)
            max_hw = arctan2((self._config.guide_size + self.sample_size) / 2.0, self.collimation_length)
            min_hw = arctan2((self._config.guide_size - self.sample_size) / 2.0, self.collimation_length)
            kernel_width = int(2 * max_hw / angle_per_pixel) + 1
            dx = linspace(-kernel_width / 2.0, kernel_width / 2.0, kernel_width)
            kernel = (
                ones(1)[:, newaxis]
                * where(
                    abs(dx) < (min_hw / angle_per_pixel),
                    1.0,
                    maximum(1.0 - (abs(dx) - min_hw / angle_per_pixel) / (max_hw - min_hw) * angle_per_pixel, 0.0),
                )[newaxis, :]
            )
            norm = kernel.sum()
            if norm == 0.0:
                return data
            kernel /= norm
            data = fftconvolve(data, kernel, mode="same")
        elif alpha:
            from scipy.signal import fftconvolve

            # implement angular resolution, vertical directly defined by size of kernel
            angle_per_pixel = arctan2(self._config.detector_size / self._config.detector_pixels, self.detector_distance)
            alpha_res = arctan2(self._config.guide_size / 2.0, self.collimation_length)
            kernel_height = int(2 * alpha_res / angle_per_pixel) + 1
            kernel = ones(kernel_height)[:, newaxis] * ones(1)[newaxis, :]
            norm = kernel.sum()
            if norm == 0.0:
                return data
            kernel /= norm
            data = fftconvolve(data, kernel, mode="same")
        return data

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
