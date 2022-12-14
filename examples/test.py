from dataclasses import dataclass

import bornagain as ba

from bornagain import deg, nm
from matplotlib import pyplot

from ba_tools import ResolutionOptions, Sample, Simulation
from ba_tools.instruments.generic import GenericSANS


@dataclass
class SpecificSample(Sample):
    def get_sample(self):
        """
        Returns a sample with spherical particles on a substrate,
        forming a hexagonal 2D lattice.
        """

        # Define materials
        material_Particle = ba.HomogeneousMaterial("Particle", 0.0006, 2e-08)
        material_Substrate = ba.HomogeneousMaterial("Substrate", 6e-06, 2e-08)
        material_Vacuum = ba.HomogeneousMaterial("Vacuum", 0, 0)

        # Define form factors
        ff = ba.FormFactorFullSphere(10 * nm)

        # Define particles
        particle = ba.Particle(material_Particle, ff)

        # Define 2D lattices
        lattice = ba.BasicLattice2D(20 * nm, 20 * nm, 120 * deg, 0)

        # Define interference functions
        iff = ba.InterferenceFunction2DLattice(lattice)
        iff_pdf = ba.FTDecayFunction2DCauchy(10 * nm, 10 * nm, 0)
        iff.setDecayFunction(iff_pdf)

        # Define particle layouts
        layout = ba.ParticleLayout()
        layout.addParticle(particle)
        layout.setInterferenceFunction(iff)
        layout.setTotalParticleSurfaceDensity(0.00288675134595)

        # Define layers
        layer_1 = ba.Layer(material_Vacuum)
        layer_1.addLayout(layout)
        layer_2 = ba.Layer(material_Substrate)

        # Define sample
        sample = ba.MultiLayer()
        sample.addLayer(layer_1)
        sample.addLayer(layer_2)

        return sample


def main():
    # defining general instrument configuration parameters, fixed during an experiment
    GenericSANS.set_config(GenericSANS.Config(center_x_pix=100, center_y_pix=15, dlambda_rel=0.1))
    # defining specific parameters for the current simulation
    inst = GenericSANS(detector_distance=5, collimation_length=5, alpha_i=2.0)

    # create sample and simulation
    smpl = SpecificSample()
    sim = Simulation(smpl, inst)
    # sim.include_specular=False

    # testing different fast resolution options
    pyplot.figure(figsize=(20, 30))

    print("sim 1")
    pyplot.subplot(421)
    pyplot.title("normal phi resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=0, alpha_bins=0, phi_bins=11))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 2")
    pyplot.subplot(422)
    pyplot.title("fast phi resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=0, alpha_bins=0, phi_bins=-1))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 3")
    pyplot.subplot(423)
    pyplot.title("normal alpha resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=0, alpha_bins=11, phi_bins=0))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 4")
    pyplot.subplot(424)
    pyplot.title("fast alpha resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=0, alpha_bins=-1, phi_bins=0))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 5")
    pyplot.subplot(425)
    pyplot.title("normal phi resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=11, alpha_bins=0, phi_bins=0))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 6")
    pyplot.subplot(426)
    pyplot.title("fast phi resolution")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=-1, alpha_bins=0, phi_bins=0))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 7")
    pyplot.subplot(427)
    pyplot.title("normal all resolutions")
    # Simulate using resolution of wavelenght, incident and azimuth angle (will take a while)
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=5, alpha_bins=11, phi_bins=11))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))

    print("sim 8")
    pyplot.subplot(428)
    pyplot.title("fast phi normal alpha/wavelength reslutions")
    res = sim.runGISANS(ResolutionOptions(wavelength_bins=5, alpha_bins=11, phi_bins=-1))
    res.plot_detector(cmap="inferno", crange=(1e-9, 1e-2))
    pyplot.show()


if __name__ == "__main__":
    main()
