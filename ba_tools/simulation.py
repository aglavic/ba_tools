"""
Generic simulation that uses a Sample and Instrument object to generate
and run the BornAgain simulation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from bornagain import (Axes, Beam, ConstantBackground, Direction, GISASSimulation, MultiLayer, ParameterDistribution,
                       deg, materialProfile)
from numpy import array, linspace, newaxis, ones, ones_like

from .experiment_base import Experiment
from .parameter_base import Parametered
from .result_object import GISASResult, OffSpecResult


@dataclass(repr=False)
class Sample(ABC, Parametered):
    """
    Derive from this abstract class to create your sample.
    It will be used for the simulation.

    Args:
        avg_material [bool]: If average material SLD is used for simulation or the one supplied for the layer.
    """

    avg_material: bool = True

    @abstractmethod
    def get_sample(self) -> MultiLayer:
        ...

    def SLD_profile(self):
        sample = self.get_sample()
        zpoints, slds = materialProfile(sample)
        return zpoints, slds


@dataclass
class ResolutionOptions:
    """
    Number of points for resolution convolution.
    Negative numbers indicate to use fast approximation.

    Fast approximation uses convolutions with the resulting image,
    it works well for phi and sometime alpha resolution of the scattered pattern
    but does not capture change in specular intensity with alpha_i.
    For wavelength the specular is always wrong, as there is no differenc
    in the scattering pattern between wavelength dependent and independent features.
    """

    wavelength_bins: int = 0
    alpha_bins: int = 0
    phi_bins: int = 0


NO_RES = ResolutionOptions(0, 0, 0)
FAST_RES = ResolutionOptions(5, 5, -1)


@dataclass
class PolarizationOptions:
    F1: bool = False
    F2: bool = False


class Simulation:
    """
    Generic simulation class creating BornAgain models
    from a sample and experiment description for a certain
    experiment.
    """

    include_specular = True

    def __init__(self, sample: Sample, experiment: Experiment):
        self.sample = sample
        self.experiment = experiment

    def SLD_profile(self):
        return self.sample.SLD_profile()

    def GISANS(self, resopts: ResolutionOptions = NO_RES):
        beam = Beam(self.experiment.I0, self.experiment.wavelength, Direction(self.experiment.alpha_i, 0.0))
        detector = self.experiment.detector
        sample = self.sample.get_sample()

        sim = GISASSimulation(beam, sample, detector)
        sim.getOptions().setIncludeSpecular(self.include_specular)

        if resopts.wavelength_bins > 0:
            wavelength_distr = self.experiment.res_wavelength
            sim.addParameterDistribution(
                ParameterDistribution.BeamWavelength, wavelength_distr, resopts.wavelength_bins
            )
        if resopts.alpha_bins > 0:
            alpha_distr = self.experiment.res_alpha
            sim.addParameterDistribution(ParameterDistribution.BeamInclinationAngle, alpha_distr, resopts.alpha_bins)
        if resopts.phi_bins > 0:
            phi_distr = self.experiment.res_phi
            sim.addParameterDistribution(ParameterDistribution.BeamAzimuthalAngle, phi_distr, resopts.phi_bins)

        # define polarization parameters from flipper 1/2 setting
        # if F1:
        #     beampol=kvector_t(0.0, -1.0, -0.0)
        # else:
        #     beampol=kvector_t(0.0, 1.0, 0.0)
        # if F2:
        #     analyzer_dir=kvector_t(0.0, -1.0, 0.0)
        # else:
        #     analyzer_dir=kvector_t(0.0, 1.0, 0.0)
        # if polarized:
        #     sim.beam().setPolarization(beampol)
        #     sim.detector().setAnalyzerProperties(analyzer_dir, 1.0, 0.5)
        # else:
        #     sim.beam().setPolarization(kvector_t(0.0, 0.0, 1.0e-6))
        #     sim.detector().setAnalyzerProperties(analyzer_dir, 0.0, 0.5)

        # if roi:
        #     roi_pos=[ri*inst.detector_pixres for ri in roi]
        #     sim.setRegionOfInterest(*roi_pos)
        # if mask:
        #     mask_pos=[mi*inst.detector_pixres for mi in mask]
        #     sim.addMask(Rectangle(*mask_pos))

        if self.experiment.Ibg != 0.0:
            sim.setBackground(ConstantBackground(self.experiment.Ibg))

        # make sure the layer average SLD is calculated correctly for the full structural model
        sim.getOptions().setUseAvgMaterials(self.sample.avg_material)
        return sim

    def runGISANS(self, resopts: ResolutionOptions = NO_RES):
        fast_wl = resopts.wavelength_bins < 0
        fast_alpha = resopts.alpha_bins < 0
        fast_phi = resopts.phi_bins < 0
        if fast_wl or fast_alpha or fast_phi:
            sim = self.GISANS(resopts)
            sim.runSimulation()
            res = sim.result()
            data = self.experiment.apply_fast_resolution(res.array(), wavelengt=fast_wl, alpha=fast_alpha, phi=fast_phi)
            return GISASResult(res, overwrite_array=data)
        else:
            sim = self.GISANS(resopts)
            sim.runSimulation()
            return GISASResult(sim.result())

    def runOffSpecular(
        self, alpha_i_axis=None, wavelength_axis=None, resopts: ResolutionOptions = NO_RES, correct_footprint=False
    ):
        """
        Offspecular simulation using user supplied scanning parameter (wavelength or angle).
        To properly include all resolution effects these are simulated separately as
        GISAS simulation.

        If correct_footprint is true, scale intensity with linear footprint correction
        using the experiment configuration as reference angle.
        """
        data = []
        alpha_f = []
        alpha_i0 = self.experiment.alpha_i
        wavelength_0 = self.experiment.wavelength
        if alpha_i_axis is None:
            alpha_i_axis = alpha_i0 * ones_like(wavelength_axis)
        if wavelength_axis is None:
            wavelength_axis = wavelength_0 * ones_like(alpha_i_axis)

        for alpha_i_j, wavelength_j in zip(alpha_i_axis, wavelength_axis):
            self.experiment.alpha_i = alpha_i_j
            self.experiment.wavelength = wavelength_j
            res = self.runGISANS(resopts)
            alpha_f.append(linspace(res.angle_limits[2], res.angle_limits[3], res.simulation.shape[1]))
            intensity = res.simulation.sum(axis=1)[::-1]
            if correct_footprint:
                intensity *= alpha_i_j / alpha_i0
            data.append(intensity)
        alpha_f = array(alpha_f) * deg
        alpha_i = alpha_i_axis[:, newaxis] * ones(alpha_f.shape[1])
        wavelength = wavelength_axis[:, newaxis] * ones(alpha_f.shape[1])

        self.experiment.alpha_i = alpha_i0
        self.experiment.wavelength = wavelength_0

        return OffSpecResult(alpha_i, alpha_f, wavelength, array(data))
