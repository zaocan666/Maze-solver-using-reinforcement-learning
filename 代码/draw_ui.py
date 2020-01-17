import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from maze import RIGHT, UP, LEFT, DOWN

class Draw_ui(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(Draw_ui,self).__init__(self.fig)
        self.axes_table = self.fig.add_subplot(121)
        self.axes_table.set_xticklabels([])
        self.axes_table.set_yticklabels([])
        self.axes_root = self.fig.add_subplot(122)
        self.axes_root.set_xticklabels([])
        self.axes_root.set_yticklabels([])

    def draw_qtable(self, qtable_model, time_, fire_flag):
        nrows, ncols = qtable_model.my_maze.maze.shape

        self.axes_table.clear()
        self.axes_table.set_xticks(np.arange(0.5, nrows + 1, step=1))
        self.axes_table.set_xticklabels([])
        self.axes_table.set_yticks(np.arange(0.5, ncols, step=1))
        self.axes_table.set_yticklabels([])
        self.axes_table.grid(True)
        aim_pos = qtable_model.my_maze.aim

        size_factor = 7.0 / qtable_model.my_maze.maze.shape[0]
        self.axes_table.plot(aim_pos[1], aim_pos[0], color='green', marker='s',
                markersize=int(30 * size_factor))  # exit is a big green square
        self.axes_table.text(aim_pos[1], aim_pos[0], "Exit", ha="center", va="center", color="white", fontSize=int(10*size_factor))

        self.axes_table.text(0, qtable_model.my_maze.maze.shape[0], "time:" + str(time_), ha="center", va="center", color="black")

        for cell in qtable_model.my_maze.free_cells:
            q = qtable_model.q_value((*cell, time_)) if qtable_model is not None else [0, 0, 0, 0]
            a = np.nonzero(q == np.max(q))[0]

            for action in a:
                dx = 0
                dy = 0
                if action == LEFT:
                    dx = -0.2
                if action == RIGHT:
                    dx = +0.2
                if action == UP:
                    dy = -0.2
                if action == DOWN:
                    dy = 0.2

                # color (red to green) represents the certainty
                color = (q[action] - -1) / (1 - -1)
                color = max(min(1, color), 0)

                self.axes_table.arrow(cell[1], cell[0], dx, dy, color=(1 - color, color, 0), head_width=0.2 * size_factor,
                         head_length=0.1 * size_factor)

        self.axes_table = self.draw_trap(self.axes_table, my_maze=qtable_model.my_maze)
        self.axes_table = self.draw_block(self.axes_table, qtable_model.my_maze.maze)
        if fire_flag:
            self.axes_table = self.draw_fire(self.axes_table, my_maze=qtable_model.my_maze)
        self.axes_table.get_figure().canvas.draw()
        #self.axes_table.get_figure().canvas.flush_events()

    def draw_root(self, my_maze, start_pos, time_, period, fire_flag):
        nrows, ncols = my_maze.maze.shape

        self.axes_root.clear()
        self.axes_root.set_xticks(np.arange(0.5, nrows + 1, step=1))
        self.axes_root.set_xticklabels([])
        self.axes_root.set_yticks(np.arange(0.5, ncols, step=1))
        self.axes_root.set_yticklabels([])
        self.axes_root.grid(True)
        aim_pos = my_maze.aim

        size_factor = 7.0 / my_maze.maze.shape[0]
        self.axes_root.plot(aim_pos[1], aim_pos[0], color='green', marker='s',markersize=int(30 * size_factor))  # exit is a big green square
        self.axes_root.text(aim_pos[1], aim_pos[0], "Exit", ha="center", va="center", color="white", fontSize=int(10*size_factor))

        self.axes_root.plot(start_pos[1], start_pos[0], color='brown', marker='s', markersize=int(30 * size_factor))
        self.axes_root.text(start_pos[1], start_pos[0], "Start", ha="center", va="center", color="white", fontSize=int(10*size_factor))

        self.axes_root.text(0, my_maze.maze.shape[0], "time:" + str(time_ % period if period != 0 else time_), ha="center",
                va="center", color="black")

        for i, cell in enumerate(my_maze.visited):
            if i + 1 >= time_ and time_ > 0:
                self.axes_root.plot(cell[1], cell[0], color='blue', marker='*', markersize=int(30 * size_factor))
                self.axes_root.text(cell[1], cell[0], "Mouse", ha="center", va="center", color="white", fontSize=int(10*size_factor))
                break
            self.axes_root.plot(cell[1], cell[0], color='yellow', marker='o',markersize=int(25 * size_factor))  # exit is a big green square
            # ax.text(cell[1], cell[0], str(i), ha="center", va="center", color="black", fontSize=int(10*size_factor))

        self.axes_root = self.draw_trap(self.axes_root, my_maze)
        if fire_flag:
            self.axes_root = self.draw_fire(self.axes_root, my_maze=my_maze)
        self.axes_root = self.draw_block(self.axes_root, my_maze.maze)
        self.axes_root.get_figure().canvas.draw()
        #self.axes_root.get_figure().canvas.flush_events()

    def draw_block(self, ax, maze):
        maze_map = np.copy(maze)
        maze_map[np.logical_and(maze != 0, maze != 1)] = 1
        ax.imshow(1 - maze_map, cmap="binary")
        return ax

    def draw_trap(self, ax, my_maze):
        size_factor = 7.0 / my_maze.maze.shape[0]
        for i, cell in enumerate(my_maze.trap):
            ax.plot(cell[1], cell[0], color='red', marker='s', markersize=int(25 * size_factor))
            ax.text(cell[1], cell[0], "Trap", ha="center", va="center", color="black", fontSize=int(10*size_factor))
        return ax

    def draw_fire(self, ax, my_maze):
        size_factor = 7.0 / my_maze.maze.shape[0]
        for i, cell in enumerate(my_maze.fire):
            ax.plot(cell[1], cell[0], color='red', marker='^', markersize=int(25 * size_factor))
            ax.text(cell[1], cell[0], "Fire", ha="center", va="top", color="black", fontSize=int(10*size_factor))
        return ax
