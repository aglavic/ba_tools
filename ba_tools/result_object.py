"""
Object that holds simulation results and defines some helpful methods
as IPython vizualizations.
"""

import bornagain as ba


class SimulationResult:
    def __init__(self, ba_result: ba.SimulationResult):
        # to prevent any low-level breaking interactions with BornAgain, copy all necessary information
        self.simulation = ba_result.array()[:]
        axis_infos = ba_result.axisInfo(ba.Axes.QSPACE)
        limits = [[axis_infos[i].m_min, axis_infos[i].m_max] for i in range(len(axis_infos))]
        self.q_limits = [v for sublist in limits for v in sublist]

        axis_infos = ba_result.axisInfo(ba.Axes.DEGREES)
        limits = [[axis_infos[i].m_min, axis_infos[i].m_max] for i in range(len(axis_infos))]
        self.angle_limits = [v for sublist in limits for v in sublist]

        axis_infos = ba_result.axisInfo(ba.Axes.MM)
        limits = [[axis_infos[i].m_min, axis_infos[i].m_max] for i in range(len(axis_infos))]
        self.mm_limits = [v for sublist in limits for v in sublist]

    def plot2d(self, limits, xlabel, ylabel, axes=None, crange=(None, None), **kwargs):
        from matplotlib import pyplot
        from matplotlib.colors import LogNorm

        if axes is None:
            axes = pyplot.gca()
        plt = axes.imshow(self.simulation, extent=limits, norm=LogNorm(*crange), **kwargs)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        pyplot.colorbar(plt)

    def plot_q(self, axes=None, **kwargs):
        self.plot2d(self.q_limits, "q$_x$ (Å$^{-1}$)", "q$_y$ (Å$^{-1}$)", axes=axes)

    def plot_angle(self, axes=None, **kwargs):
        self.plot2d(self.angle_limits, "$\\phi_f$ (°)", "$2\\theta_f$ (°)", axes=axes)

    def plot_detector(self, axes=None, **kwargs):
        self.plot2d(self.mm_limits, "X (mm)", "Y (mm)", axes=axes)

    def _repr_html_(self):
        from IPython.display import display_html
        from matplotlib import pyplot

        self.plot_q()
        return "Simulation Result"
