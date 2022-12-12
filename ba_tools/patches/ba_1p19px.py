"""
"""

from logging import debug

import bornagain as ba

debug("patching R3 -> kvector_t")
ba.kvector_t = ba.R3
debug("patching ScatteringSimulation -> GISASSimulation")
ba.GISASSimulation = ba.ScatteringSimulation

for aname in dir(ba):
    if aname.startswith("Profile"):
        setattr(ba, f"FTDecayFunction{aname[7:]}", getattr(ba, f"{aname}"))
        debug(f"patching {aname} -> FTDecayFunction{aname[7:]}")
    if aname.startswith("Interference"):
        setattr(ba, f"InterferenceFunction{aname[12:]}", getattr(ba, f"{aname}"))
        debug(f"patching {aname} -> InterferenceFunction{aname[12:]}")

# fix method names
debug("patching ParticleLayout.setInterference -> ParticleLayout.setInterferenceFunction")
ba.ParticleLayout.setInterferenceFunction = ba.ParticleLayout.setInterference
debug("patching ScatteringSimulation.options -> ScatteringSimulation.getOptions")
ba.ScatteringSimulation.getOptions = ba.ScatteringSimulation.options
