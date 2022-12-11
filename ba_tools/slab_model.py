"""
Simplified way of describing layers and materials for quick building of
multilayers with roughness.
"""
from dataclasses import dataclass
from typing import List

from bornagain import angstrom, MaterialBySLD, Layer, RangedDistributionGaussian, LayerRoughness, MultiLayer
from .simulation import Sample
from .parameter_base import pp, Parametered

@dataclass
class SLayer(Parametered):
    name: str
    nSLD: complex = pp(1e-6+0j, 'AA^-2', 1.0)
    xSLD: complex = pp(1e-6+0j, 'AA^-2', 1.0)
    thickness: float = pp(1.0, 'nm')
    roughness: float = pp(0.0, 'nm')

@dataclass
class Slab(Parametered):
    """
    Class holding the layer information from specular reflectivity. Contains the layer thicknesses,
    SLDs and roughnesses for both x-rays and neutrons.

    Model is build from a list of SLayers, starting with ambience:
        Slabs(layers=[
        #         name    ,   nSLD,         xSLD, thickness, roughness
        SLayer(  'ambient',     0.,           0.,      None, None),
        SLayer(   'layer1',   3e-6, 2.0e-5+3e-8j,      None, None),
        SLayer(   'layer2',   5e-6, 2.3e-5+3e-8j,      None, None),
        SLayer('substrate',   2e-6,   4e-5+3e-8j,      None, None),
        ]
        )
    """
    layers: List[SLayer]
    hurst: float = 0.3
    corr: float = pp(500.0, 'nm')

    def __post_init__(self):
        super().__post_init__()
        if len(self.layers)<2:
            raise ValueError("Ambient and substrate layer required but length of layers < 2")
        keys=[]
        for layer in self.layers:
            if not isinstance(layer, SLayer):
                raise ValueError("Each layer has to be of type SLayer")
            if layer.name in keys:
                raise ValueError("Each layer has to have a unique name")
            # convert possible float falues to complex
            layer.nSLD = complex(layer.nSLD)
            layer.xSLD = complex(layer.xSLD)
            keys.append(layer.name)

    def resolve_layers(self, neutron=True):
        output=[]
        for li in self.layers:
            if neutron:
                material=MaterialBySLD(li.name, li.nSLD.real, li.nSLD.imag)
            else:
                material=MaterialBySLD(li.name, li.xSLD.real, li.xSLD.imag)
            if li.thickness == 0.0:
                layer=Layer(material)
            else:
                layer=Layer(material, li.thickness)
            if li.sigma is None:
                output.append([li.name, layer])
            else:
                roughness=LayerRoughness(li.sigma, self.hurst, self.corr)
                output.append([li.name, layer, roughness])
        return output

    def add_layers(self, sample: MultiLayer, neutron: bool=True):
        layers=self.resolve_layers(neutron=neutron)
        for li in layers:
            if len(li)==2:
                sample.addLayer(li[1])
            else:
                sample.addLayerWithTopRoughness(li[1], li[2])

    def _repr_pretty_(self):
        output='SlabModel(\n    layers=\n'
        for li in self.layers:
            output+="           SLayer(% 16s, % 20s, % 20s, % 12s, % 12s),\n"%("'%s'"%li.name, li.nSLD, li.xSLD,
                                                                   li.thickness, li.sigma)
        output+=f'           ], hurst={self.hurst}, corr={self.corr})'
        return output

@dataclass
class SlabModel(Sample):
    slab: Slab = None
    neutron: bool = True

    def get_sample(self):
        sample=MultiLayer()
        self.slab.add_layers(sample, neutron=self.neutron)
        return sample
