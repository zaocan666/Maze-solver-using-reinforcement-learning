import matplotlib.pyplot as plt
import numpy as np
from maze import RIGHT, UP, LEFT, DOWN

def draw_qtable(ax, qtable_model, time_, fire_flag):
    nrows, ncols = qtable_model.my_maze.maze.shape

    ax.clear()
    ax.set_xticks(np.arange(0.5, nrows+1, step=1))
    ax.set_xticklabels([])
    ax.set_yticks(np.arange(0.5, ncols, step=1))
    ax.set_yticklabels([])
    ax.grid(True)
    aim_pos = qtable_model.my_maze.aim

    size_factor = 7.0 / qtable_model.my_maze.maze.shape[0]
    ax.plot(aim_pos[1], aim_pos[0], color = 'green', marker = 's', markersize=int(30*size_factor))  # exit is a big green square
    ax.text(aim_pos[1], aim_pos[0], "Exit", ha="center", va="center", color="white")

    ax.text(0, qtable_model.my_maze.maze.shape[0], "time:"+str(time_), ha="center", va="center", color="black")

    for cell in qtable_model.my_maze.free_cells:
        q = qtable_model.q_value((*cell,time_)) if qtable_model is not None else [0, 0, 0, 0]
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

            ax.arrow(cell[1], cell[0], dx, dy, color=(1 - color, color, 0), head_width=0.2*size_factor, head_length=0.1*size_factor)

    ax = draw_trap(ax, my_maze=qtable_model.my_maze)
    ax = draw_block(ax, qtable_model.my_maze.maze)
    if fire_flag:
        ax = draw_fire(ax, my_maze=qtable_model.my_maze)
    ax.get_figure().canvas.draw()

def draw_root(ax, my_maze, start_pos, time_, period, fire_flag):
    nrows, ncols = my_maze.maze.shape

    ax.clear()
    ax.set_xticks(np.arange(0.5, nrows+1, step=1))
    ax.set_xticklabels([])
    ax.set_yticks(np.arange(0.5, ncols, step=1))
    ax.set_yticklabels([])
    ax.grid(True)
    aim_pos = my_maze.aim

    size_factor = 7.0 / my_maze.maze.shape[0]
    ax.plot(aim_pos[1], aim_pos[0], color='green', marker='s', markersize=int(30*size_factor))  # exit is a big green square
    ax.text(aim_pos[1], aim_pos[0], "Exit", ha="center", va="center", color="white")

    ax.plot(start_pos[1], start_pos[0], color='brown', marker='s', markersize=int(30*size_factor))
    ax.text(start_pos[1], start_pos[0], "Start", ha="center", va="center", color="white")

    ax.text(0, my_maze.maze.shape[0], "time:" + str(time_%period if period!=0 else time_), ha="center", va="center", color="black")

    for i, cell in enumerate(my_maze.visited):
        if i+1>=time_ and time_>0:
            ax.plot(cell[1], cell[0], color='blue', marker='*', markersize=int(30 * size_factor))
            ax.text(cell[1], cell[0], "Mouse", ha="center", va="center", color="white")
            break
        ax.plot(cell[1], cell[0], color='yellow', marker='o', markersize=int(25*size_factor))  # exit is a big green square
        #ax.text(cell[1], cell[0], str(i), ha="center", va="center", color="black")

    ax=draw_trap(ax, my_maze)
    if fire_flag:
        ax = draw_fire(ax, my_maze=my_maze)
    ax = draw_block(ax, my_maze.maze)
    ax.get_figure().canvas.draw()

def draw_block(ax, maze):
    maze_map = np.copy(maze)
    maze_map[np.logical_and(maze != 0, maze != 1)] = 1
    ax.imshow(1 - maze_map, cmap="binary")
    return ax

def draw_trap(ax, my_maze):
    size_factor = 7.0 / my_maze.maze.shape[0]
    for i, cell in enumerate(my_maze.trap):
        ax.plot(cell[1], cell[0], color='red', marker='s', markersize=int(40*size_factor))
        ax.text(cell[1], cell[0], "Trap", ha="center", va="center", color="black")
    return ax

def draw_fire(ax, my_maze):
    size_factor = 7.0 / my_maze.maze.shape[0]
    for i, cell in enumerate(my_maze.fire):
        ax.plot(cell[1], cell[0], color='red', marker='^',markersize=int(40 * size_factor))
        ax.text(cell[1], cell[0], "Fire", ha="center", va="center", color="black")
    return ax

def draw_table_root_byTime(qtable_model, my_maze, start_pos):
    fig1, ax1 = plt.subplots(1, 1, tight_layout=True)
    fig1.canvas.set_window_title("QTable")

    fig2, ax2 = plt.subplots(1, 1, tight_layout=True)
    fig2.canvas.set_window_title("Root")

    plt.show(block=False)

    time_ = 0
    period = qtable_model.my_maze.period
    while True:
        if period!=0 and (time_%period)>=period/2: fire_flag=True
        else: fire_flag=False

        draw_qtable(ax1, qtable_model, time_%period if period!=0 else 0, fire_flag)
        draw_root(ax2, my_maze, start_pos,time_, period, fire_flag)

        time_ = time_+1

        if time_>=len(qtable_model.my_maze.visited)+2:
            time_=0
        plt.pause(0.3)