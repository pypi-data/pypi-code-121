import math
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
from mpl_toolkits import mplot3d

from nbodysim import nmath as nm

from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')

class OrbitPlotter:
    """
    Class used to plot the results of using an integrator
    """
    def __init__(self, integrator, seed = 42, animation_steps = 1, twodims = True, grid = False):
        """
        :param integrator: Integrator instance which has calculated orbits
        :param seed: used as seed to generate the colours of the plot
        :param animation_steps: number of steps to consider per frame of animation
        :param twodims: if True, will plot the orbit using 2 dimensions (x and y)
        :param grid: if True, will plot in 2 dimensions,
                     whilst displaying information, such as energy, angular momentum, position and velocity change across time
        """

        self.integrator = integrator
        self.seed = seed
        self.animation_steps = animation_steps
        self.twodims = twodims
        self.grid = grid

        # take properties of Integrator (used in calculations when plotting)
        self.n = integrator.nbody.n
        self.position_orbit = integrator.position_orbit
        self.delta = integrator.delta
        self.steps = integrator.steps

        # generate colours for the orbits
        self.colours = self.generate_colour()

        # calculate all the times at which the orbit positions/velocities were calculated
        # if adaptive, times are calculated within the integration
        self.times = self.integrator.times if self.integrator.adaptive else np.array([i*self.delta for i in range(self.steps)])

        # set up the figure for plotting
        self.set_fig()

    def generate_colour(self):
        """
        Uses the seed from init to generate a random list of n colours, one for each orbit
        """
        random.seed(self.seed)
        colours = []

        for i in range(self.n):
            r = random.random()
            g = random.random()
            b = random.random()
            colours.append((r, g, b))

        return colours

    def set_fig(self):
        """
        Sets up the fig on which the plots are drawn.
        If grid = True, we use GridSpec to be able to display not only the orbits,
        but values such as positions, velocities, energies and angular momentum.
        Otherwise, if twodims = True, we set a 2D plot, and if twodims = False, we set a 3D plot.
        """

        if not self.grid:
            if self.twodims:
                self.fig, self.ax = plt.subplots()
            else:
                self.fig = plt.figure()
                self.ax = plt.axes(projection="3d")
        else:
            self.fig = plt.figure(figsize = (14, 8))
            self.gs = GridSpec(nrows = 3, ncols = 5, figure = self.fig)

        # set window title
        self.fig.canvas.set_window_title("Vacation Scholarship - N-Body Problem")

# ---------------------------------------- ANIMATED PLOTS ----------------------------------------

    def animation_func_orbit_3D(self, frame):
        """
        Function for drawing a frame in a 3D animation
        :param frame: the frame in animation to draw on
        """

        # clear the plot
        plt.cla()

        # for each body, plot frame * animation_steps steps in the orbit
        for i,orbit in enumerate(self.position_orbit[:,:frame*self.animation_steps,:]):
            # display the legend only for the last frame
            if frame == self.n - 1:
                self.ax.plot3D(orbit[:,0], orbit[:,1], orbit[:,2], label = f"Orbit {i+1}", c = self.colours[i])
                self.ax.legend()
            else:
                self.ax.plot3D(orbit[:,0], orbit[:,1], orbit[:,2], c = self.colours[i])

            # display the position of the body at the end of the plotted interval
            # gives an idea of the direction in which the bodies are moving
            if (len(orbit) > 0):
                self.ax.scatter3D(orbit[-1, 0], orbit[-1, 1], orbit[-1,2], c = self.colours[i], s=10)

        # display time of the simulation only for constant timestep
        if not self.integrator.adaptive:
            self.ax.annotate(f"t = {round(frame * self.delta * self.animation_steps, 1)}", xy=self.integrator.nbody.com[:2])

    def animation_func_orbit_2D(self, frame):
        """
        Function for drawing a frame in a 2D animation
        :param frame: the frame in animation to draw on
        """

        # clear the plot
        plt.cla()

        # for each body, plot frame * animation_steps steps in the orbit
        for i,orbit in enumerate(self.position_orbit[:,:np.int(np.floor(frame*self.animation_steps)),:]):
            # display the legend only for the last frame
            if frame == self.n - 1:
                self.ax.plot(orbit[:,0], orbit[:,1], label = f"Orbit {i+1}", c = self.colours[i])
                self.ax.legend()
            else:
                self.ax.plot(orbit[:,0], orbit[:,1], c = self.colours[i])

            # display the position of the body at the end of the plotted interval
            # gives an idea of the direction in which the bodies are moving
            if (len(orbit) > 0):
                self.ax.scatter(orbit[-1, 0], orbit[-1, 1], c = self.colours[i], s=10)

        # create title for plot
        self.ax.set_title(f"Trajectories for a {self.n}-body Problem")

        # display time of the simulation only for constant timestep
        if not self.integrator.adaptive:
            self.ax.annotate(f"t = {round(frame * self.delta * self.animation_steps, 1)}", xy=self.integrator.nbody.com[:2])

    def animate_orbit(self, xlims = (-5,5), ylims = (-5,5)):
        """
        Creates and shows the animated orbits from the simulations
        :param xlims: tuple giving the x limit for the plotting
        :param ylims: tuple giving the y limit for the plotting
        """

        assert (not self.grid)

        if self.twodims:
            # create 2D animation
            animator = FuncAnimation(self.fig, self.animation_func_orbit_2D,
                                     frames = math.ceil(self.steps/self.animation_steps), repeat = False, interval = 100)

            # x and y axes are same size
            plt.axis("equal")
        else:
            # create 3D animation
            animator = FuncAnimation(self.fig, self.animation_func_orbit_3D,
                                     frames = math.ceil(self.steps/self.animation_steps), repeat = False, interval = 100)

            # label the z axis (since we are considering 3D plotting)
            self.ax.set_zlabel("z")

        # set plot properties
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")

        # display animation
        plt.show()

# ---------------------------------------- STATIONARY PLOT ----------------------------------------

    def plot_orbit(self, xlims = (-5,5), ylims = (-5,5), size = 50):
        """
        Plots the orbit calculated from the integrator as a standard plot
        :param xlims: tuple giving the x limit for the plotting
        :param ylims: tuple giving the y limit for the plotting
        :param size: size of the scatter marks in the plot
        """

        assert (not self.grid)

        if self.twodims:
            # plot in 2D each orbit, alongisde the start and end points
            for i, orbit in enumerate(self.position_orbit):
                self.ax.plot(orbit[:, 0], orbit[:, 1], label=f"Orbit {i + 1}", c=self.colours[i])
                self.ax.scatter(orbit[0, 0], orbit[0, 1], c=self.colours[i], s = size, marker="^")
                self.ax.scatter(orbit[-1, 0], orbit[-1, 1], c=self.colours[i], s = size)
                self.ax.set_title(f"Trajectories for a {self.n}-body Problem")
                # plot the orbits produced by the simulation
        
            
        else:
            # plot in 3D each orbit, alongisde the start and end points
            for i,orbit in enumerate(self.position_orbit):
                self.ax.plot3D(orbit[:,0], orbit[:,1], orbit[:,2], label = f"Orbit {i+1}", c = self.colours[i])
                self.ax.scatter3D(orbit[0, 0], orbit[0, 1], orbit[0, 2], c = self.colours[i], s = size, marker = "^")
                self.ax.scatter3D(orbit[-1, 0], orbit[-1, 1], orbit[-1, 2], c = self.colours[i], s = size)
                self.ax.set_title(f"Trajectories for a {self.n}-body Problem", pad=40)
                self.ax.set_zlabel("z")

        # set plot properties
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.axis("equal")
        self.ax.legend()

        # display plot
        plt.show()

# ---------------------------------------- GRID PLOTS ----------------------------------------

    def plot_energies(self, ax, absolute = False, e_components = False):
        """
        Used to display energies across time when plotting in grid mode
        :param ax: the axis object on which the energies are plotted
        :param absolute: if True, displays the values of energy across time.
                         if False, displays the percentage error in the value of energy across time
        :param e_components: if True, shows not only total energy, but also kinetic and GPE
        """

        if absolute:
            # plot energy across time
            ax.plot(self.times, self.integrator.historic_energy, label = "Total Energy", c = "k")

            # if required, plot kinetic and gravitational potential energies
            if e_components:
                ax.plot(self.times, self.integrator.historic_kinetic_energy, label="Kinetic Energy", c = "r")
                ax.plot(self.times, self.integrator.historic_gpe, label="Gravitational Potential Energy", c = "b")

            # set plot properties
            ax.set_title("Energy Change")
            ax.set_xlabel("Time")
            ax.set_ylabel("Energy")
            ax.legend()
        else:
            # plot percentage error in energy across time
            ax.plot(self.times,
                    nm.perc_change(self.integrator.historic_energy[0], self.integrator.historic_energy, perc = True),
                    c = "k")

            # set plot properties
            ax.set_title("Percentage Energy Error")
            ax.set_xlabel("Time")
            ax.set_ylabel("Percentage Error")

    def plot_angular_momentum(self, ax, absolute = False, dim = 2):
        """
        NOTE: THIS METHOD WILL CHANGE WHEN MORE COMPLEX ORBITS ARE CALCULATED,
        AS ANGULAR MOMENTUM WILL NOT ONLY OCCUR IN A SINGLE DIMENSION
        Used to display angular momentum across time when plotting in grid mode
        :param ax: the axis object on which the angular momentum is plotted
        :param absolute: if True, displays the value of angular momentum across time.
                         if False, displays the percentage error in the value of angular momentum across time
        :param dim: the component (x, y or z) of angular momentum to consider
        """

        # get the component of angular momentum according to dim
        # for orbits over the x and y plane, this will be the z direction
        amomentum_z = self.integrator.historic_angular_momentum[:,dim]

        # plot angular momentum either across time, or as percentage error over time
        if absolute:
            ax.plot(self.times, amomentum_z, c="k")
            ax.set_title("Angular Momentum Change")
            ax.set_ylabel("Angular Momentum")
        else:
            ax.plot(self.times, nm.perc_change(amomentum_z[0], amomentum_z, perc=True, init_val=100), c="k")
            ax.set_title("Percentage Angular Momentum Error")
            ax.set_ylabel("Percentage Error")

        ax.set_xlabel("Time")


    def plot_adaptive_delta(self, ax):
        """
        Used to display adaptive delta across time when plotting in grid mode
        :param ax: the axis object on which the angular momentum is plotted
        """

        ax.plot(self.times, self.integrator.historic_delta)
        ax.set_title("Adaptive Delta Change")
        ax.set_xlabel("Time")
        ax.set_ylabel(r"$\Delta t$")

    def plot_dim(self, data, dim, ax, title, legend = False):
        """
        Used to display raw data from a tensor, across one of its dimensions.
        For example, to plot the x position of all the orbits across the simulation,
        as data we would use the position_orbit tensor and dim = 0
        :param data: the tensor containing data to be plotted
        :param dim: the dimension of the tensor to plot
        :param ax: the axis object on which the angular momentum is plotted
        :param title: title for the plot
        :param legend: if True, displays a legend for the plot
        :return:
        """

        # check: the plotting dimension is within the size of the coordinate system
        assert dim < data.shape[-1]

        # extract the data for plotting, according to the desired dimension
        dim_data = data[:,:,dim]

        # ensure tha plotting data is of the expected shape
        assert dim_data.shape == (self.n, self.steps), f"Expected data shape: {(self.n, self.steps)}\n" \
                                                       f"Actual data shape: {dim_data.shape}"

        # for each body in the simulation, plot the approriate data
        for i in range(len(dim_data)):
            ax.plot(self.times, dim_data[i], label = f"Orbit {i + 1}", c = self.colours[i])

        # set plot properties
        ax.set_title(f"{title} Change")
        ax.set_xlabel("Time")
        ax.set_ylabel(title)

        # display legend if required
        if legend:
            ax.legend(loc = "upper right")

    def plot_grid(self, xlims = (-5,5), ylims = (-5,5)):
        """
        Plots the simulation results as a grid containing the resulting orbits, changes in x, y, z position and velocity,
        alongside change in energy and angular momentum (and adaptive delta)
        :param xlims: tuple giving the x limit for the plotting
        :param ylims: tuple giving the y limit for the plotting
        """

        assert self.grid, "To display a grid with the orbit information, initialise OrbitPlotter with grid = True"

        # generate axes objects to plot on
        ax_orbit = self.fig.add_subplot(self.gs[0:2, 0:2])

        ax_position_x = self.fig.add_subplot(self.gs[0,2])
        ax_position_y = self.fig.add_subplot(self.gs[0, 3])
        ax_position_z = self.fig.add_subplot(self.gs[0, 4])

        ax_velocity_x = self.fig.add_subplot(self.gs[1, 2])
        ax_velocity_y = self.fig.add_subplot(self.gs[1, 3])
        ax_velocity_z = self.fig.add_subplot(self.gs[1, 4])

        ax_energy = self.fig.add_subplot(self.gs[2, 0:2])
        ax_amomentum = self.fig.add_subplot(self.gs[2, 3:])

        # plot the orbits produced by the simulation
        for i, orbit in enumerate(self.position_orbit):
            ax_orbit.plot(orbit[:, 0], orbit[:, 1], label=f"Orbit {i + 1}", c = self.colours[i])
            ax_orbit.scatter(orbit[0, 0], orbit[0, 1], c = self.colours[i], s=10, marker="^")
            ax_orbit.scatter(orbit[-1, 0], orbit[-1, 1], c = self.colours[i], s = 10)#*self.integrator.nbody.masses[i])
        ax_orbit.set_title(f"Trajectories for a {self.n}-body Problem")
        ax_orbit.axis("equal")
        ax_orbit.legend()

        # plot energy and angular momentum over time
        self.plot_energies(ax_energy, absolute = False, e_components = True)
        self.plot_angular_momentum(ax_amomentum, absolute = False, dim = 2)

        # plot positions over time
        self.plot_dim(self.position_orbit, dim = 0, ax = ax_position_x, title = r"Position $x$")
        self.plot_dim(self.position_orbit, dim = 1, ax = ax_position_y, title = r"Position $y$")
        self.plot_dim(self.position_orbit, dim = 2, ax = ax_position_z, title = r"Position $z$")

        # plot velocities over time
        self.plot_dim(self.integrator.velocity_orbit, dim = 0, ax=ax_velocity_x, title = r"Velocity $x$")
        self.plot_dim(self.integrator.velocity_orbit, dim = 1, ax = ax_velocity_y, title = r"Velocity $y$")
        self.plot_dim(self.integrator.velocity_orbit, dim = 2, ax = ax_velocity_z, title = r"Velocity $z$")

        # if required, plot the adaptive delta
        if self.integrator.adaptive:
            ax_delta = self.fig.add_subplot(self.gs[2,2])
            self.plot_adaptive_delta(ax_delta)

        # display the grid plots
        plt.tight_layout()
        plt.show()
