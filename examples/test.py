from dataclasses import dataclass

import bornagain as ba
from bornagain import nm, deg

from matplotlib import pylab

from ba_tools import Sample, Simulation, ResolutionOptions
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
    from bornagain import ba_plot

    inst = GenericSANS(detector_distance=8, collimation_length=8, alpha_i=0.25)

    smpl = SpecificSample()
    sim = Simulation(smpl, inst)
    #sim.include_specular=False
    sim = sim.GISANS(ResolutionOptions(wavelength_bins=5, alpha_bins=11, phi_bins=11))
    ba_plot.run_and_plot(sim)


if __name__ == "__main__":
    main()
