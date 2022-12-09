"""
Generic simulation that uses a Sample and Instrument object to generate
and run the BornAgain simulation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from bornagain import Beam, ConstantBackground, Direction, DistributionTrapezoid, GISASSimulation, MultiLayer

from .experiment_base import Experiment


class Sample(ABC):
    """
    Derive from this abstract class to create your sample.
    It will be used for the simulation.
    """

    avg_material: bool = True  # use average material for layers in simulation

    @abstractmethod
    def get_sample(self) -> MultiLayer:
        ...


@dataclass
class ResolutionOptions:
    wavelength_bins: int = 0
    alpha_bins: int = 0
    phi_bins: int = 0


NO_RES = ResolutionOptions(0, 0, 0)


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

    def GISANS(self, resopts: ResolutionOptions = NO_RES):
        beam = Beam(self.experiment.I0, self.experiment.wavelength, Direction(self.experiment.alpha_i, 0.0))
        detector = self.experiment.detector
        sample = self.sample.get_sample()

        sim = GISASSimulation(beam, sample, detector)
        sim.getOptions().setIncludeSpecular(self.include_specular)

        if resopts.wavelength_bins:
            wavelength_distr = self.experiment.res_wavelength
            sim.addParameterDistribution("*/Beam/Wavelength", wavelength_distr, resopts.wavelength_bins)
        if resopts.alpha_bins:
            alpha_distr = self.experiment.res_alpha
            sim.addParameterDistribution("*/Beam/InclinationAngle", alpha_distr, resopts.alpha_bins)
        if resopts.phi_bins:
            phi_distr = self.experiment.res_phi
            sim.addParameterDistribution("*/Beam/AzimuthalAngle", phi_distr, resopts.phi_bins)

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
