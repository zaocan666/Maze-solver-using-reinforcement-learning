from maze import Maze, show_maze
from git import Git, NUM_ACTION
import random
import numpy as np
import json
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.advanced_activations import PReLU

max_save_size = 1000
epoch_num = 15000
model_file = ""
save_file = "saved_weight/first_simple"
data_size = 50

def play_game(model, my_maze, rat_cell):
    my_maze.reset(rat_cell)
    envstate = my_maze.get_current_state()
    while True:
        prev_envstate = envstate
        # get next action
        q = model.predict(prev_envstate)
        action = np.argmax(q[0])

        # apply action, get rewards and new state
        envstate, reward, game_status = my_maze.act(action)
        if game_status == 'win':
            return True
        elif game_status == 'lose':
            return False

def completion_check(model, qmaze):
    for cell in qmaze.free_cells:
        if not qmaze.valid_actions(cell):
            return False
        if not play_game(model, qmaze, cell):
            return False
    return True

def train(model, maze, epsilon = 0.1):
    if model_file:
        print("loading weights from file: %s" % (model_file,))
        model.load_weights(model_file)

    my_maze = Maze(maze)

    # 存储episode
    git_store = Git(model, max_save_size=max_save_size)

    win_history = []
    hsize = my_maze.maze.size//2
    win_rate = 0.0

    for epoch in range(epoch_num):
        loss = 0.0
        rat_cell = random.choice(my_maze.free_cells)
        my_maze.reset(rat_cell)
        game_over = False

        state = my_maze.get_current_state()

        n_episodes = 0
        while not game_over:
            valid_actions = my_maze.valid_actions()
            if not valid_actions: break
            state_now = state

            # epsilon-贪心算法
            if np.random.rand() < epsilon:
                action = random.choice(valid_actions)
            else:
                action = np.argmax(git_store.predict(state_now))

            # 实施action
            state_next, reward, game_status = my_maze.act(action, my_maze.get_current_state)
            if game_status == 'win':
                win_history.append(1)
                game_over = True
            elif game_status == 'lose':
                win_history.append(0)
                game_over = True
            else:
                game_over = False

            #保存episode
            episode = [state_now, action, reward, state_next, game_over]
            git_store.remember(episode)
            n_episodes += 1

            # 训练网络
            inputs, targets = git_store.get_data(batch_size=data_size)
            h = model.fit(
                inputs,
                targets,
                epochs=8,
                batch_size=16,
                verbose=0,
            )
            loss = model.evaluate(inputs, targets, verbose=0)

        if len(win_history) > hsize:
            win_rate = sum(win_history[-hsize:]) / hsize

        template = "Epoch: {:03d}/{:d}  Loss: {:.4f}    Episodes: {:d}  Win count: {:d} Win rate: {:.3f}"
        print(template.format(epoch, epoch_num-1, loss, n_episodes, sum(win_history), win_rate))

        # Save trained model weights and architecture, this will be used by the visualization code
        h5file = save_file + ".h5"
        json_file = save_file + ".json"
        model.save_weights(h5file, overwrite=True)
        with open(json_file, "w") as outfile:
            json.dump(model.to_json(), outfile)

        # we simply check if training has exhausted all free cells and if in all
        # cases the agent won
        if win_rate > 0.9: epsilon = 0.05
        '''if sum(win_history[-hsize:]) == hsize and completion_check(model, my_maze):
            print("Reached 100%% win rate at epoch: %d" % (epoch,))
            break'''

    print('files: %s, %s' % (h5file, json_file))
    print("n_epoch: %d, max_mem: %d, data: %d, time: %s" % (epoch, max_save_size, data_size))

def build_model(maze, lr=0.001):
    model = Sequential()
    model.add(Dense(maze.size, input_shape=(maze.size,)))
    model.add(PReLU())
    model.add(Dense(maze.size))
    model.add(PReLU())
    model.add(Dense(NUM_ACTION))
    model.compile(optimizer='adam', loss='mse')
    return model

if __name__=="__main__":
    maze = np.array([
        [1., 0., 1., 1., 1., 1., 1.],
        [1., 1., 1., 0., 0., 1., 0.],
        [0., 0., 0., 1., 1., 1., 0.],
        [1., 1., 1., 1., 0., 0., 1.],
        [1., 0., 0., 0., 1., 1., 1.],
        [1., 0., 1., 1., 1., 1., 1.],
        [1., 1., 1., 0., 1., 1., 1.]
    ])

    my_maze = Maze(maze_map=maze)
    model = build_model(maze)
    train(model, maze)