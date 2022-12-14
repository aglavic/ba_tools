"""
Object that holds simulation results and defines some helpful methods
as IPython vizualizations.
"""

import bornagain as ba
import numpy as np

from bornagain import angstrom
from numpy.typing import NDArray


class SimulationReult:
    simulation: NDArray

    def plot_q(self):
        raise NotImplementedError("plot_q has to be defined in subclass")

    def plot2d(self, limits, xlabel, ylabel, axes=None, log=True, crange=(None, None), **kwargs):
        from matplotlib import pyplot
        from matplotlib.colors import LogNorm, Normalize

        if axes is None:
            axes = pyplot.gca()
        if log:
            plt = axes.imshow(self.simulation, extent=limits, norm=LogNorm(*crange), **kwargs)
        else:
            plt = axes.imshow(self.simulation, extent=limits, norm=Normalize(*crange), **kwargs)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        pyplot.colorbar(plt)

    def plot2dm(self, X, Y, xlabel, ylabel, axes=None, log=True, crange=(None, None), **kwargs):
        from matplotlib import pyplot
        from matplotlib.colors import LogNorm, Normalize

        if axes is None:
            axes = pyplot.gca()
        if log:
            plt = axes.pcolormesh(X, Y, self.simulation, norm=LogNorm(*crange), **kwargs)
        else:
            plt = axes.pcolormesh(X, Y, self.simulation, norm=Normalize(*crange), **kwargs)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        pyplot.colorbar(plt)

    def _repr_html_(self):
        self.plot_q()
        return f"{self.__class__.__qualname__}"


class GISASResult(SimulationReult):
    def __init__(self, ba_result: ba.SimulationResult, overwrite_array: NDArray = None):
        # to prevent any low-level breaking interactions with BornAgain, copy all necessary information
        if overwrite_array is not None:
            self.simulation = overwrite_array[:]
        else:
            self.simulation = ba_result.array()[:]
        axis_infos = ba_result.axisInfo(ba.Axes.QSPACE)
        limits = [[axis_infos[i].m_min, axis_infos[i].m_max] for i in range(len(axis_infos))]
        self.q_limits = [v for sublist in limits for v in sublist]

        axis_infos = ba_result.axisInfo(ba.Axes.DEGREES)
        limits = [[axis_infos[i].m_min, axis_infos[i].m_max] for i in range(len(axis_infos))]
        self.angle_limits = [v for sublist in limits for v in sublist]

        axis_infos = ba_result.axisInfo(ba.Axes.MM)
        limits = [
            [axis_infos[i].m_min / ba.millimeter, axis_infos[i].m_max / ba.millimeter] for i in range(len(axis_infos))
        ]
        self.mm_limits = [v for sublist in limits for v in sublist]

    def plot_q(self, axes=None, log=True, crange=(None, None), **kwargs):
        self.plot2d(self.q_limits, "q$_x$ (Å$^{-1}$)", "q$_y$ (Å$^{-1}$)", axes=axes, log=log, crange=crange, **kwargs)

    def plot_angle(self, axes=None, log=True, crange=(None, None), **kwargs):
        self.plot2d(self.angle_limits, "$\\phi_f$ (°)", "$\\alpha_f$ (°)", axes=axes, log=log, crange=crange, **kwargs)

    def plot_detector(self, axes=None, log=True, crange=(None, None), **kwargs):
        self.plot2d(self.mm_limits, "X (mm)", "Y (mm)", axes=axes, log=log, crange=crange, **kwargs)


class OffSpecResult(SimulationReult):
    def __init__(self, alpha_i: NDArray, alpha_f: NDArray, wavelengths: NDArray, data: NDArray):
        # to prevent any low-level breaking interactions with BornAgain, copy all necessary information
        self.simulation = np.asarray(data)
        wavelengths = wavelengths / angstrom

        self.pi = 2.0 * np.pi / wavelengths * np.sin(alpha_i)
        self.pf = 2.0 * np.pi / wavelengths * np.sin(alpha_f)

    def plot_q(self, axes=None, log=True, crange=(None, None), **kwargs):
        self.plot2dm(
            self.pi, self.pf, "p$_i$-p$_f$ (Å$^{-1}$)", "q$_z$ (Å$^{-1}$)", axes=axes, log=log, crange=crange, **kwargs
        )
