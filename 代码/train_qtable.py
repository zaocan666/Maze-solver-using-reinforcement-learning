from maze import Maze, ACTIONS
from draw import draw_qtable, draw_root, draw_table_root_byTime
from maze_map import Mazes

import random
import numpy as np
import matplotlib.pyplot as plt
import json

NUM_ACTION=4
epoch_num = 30000
save_file = "saved_weight/first_simple"
data_size = 50

class QTableModel(object):
    def __init__(self, my_maze, epsilon=0.1, learning_rate = 0.1, gamma = 0.9):
        self.Q_table = dict()
        self.my_maze = my_maze
        self.eqsilon_ = epsilon
        self.hsize = my_maze.maze.size//2
        self.learning_rate = learning_rate
        self.gamma = gamma

    def q_value(self, state):
        return np.array([self.Q_table.get((state, action), 0.0) for action in ACTIONS])

    def predict(self, state):
        return ACTIONS[np.argmax(self.q_value(state))]

    def train(self, output_line=None, main_ui=None, epoch_N = epoch_num):
        self.Q_table = dict()
        win_history = []
        win_rate = 0.0

        for epoch in range(epoch_N):
            if self.my_maze.period==0:
                rat_cell = random.choice(self.my_maze.free_cells)
            else:
                rat_cell = (0,0)
            self.my_maze.reset(rat_cell,0)
            game_over = False

            state = self.my_maze.get_current_state_simple()

            n_episodes = 0
            while not game_over:
                valid_actions = self.my_maze.valid_actions()
                if not valid_actions: break
                state_now = state

                # epsilon-贪心算法
                if np.random.rand() < self.eqsilon_:
                    action = random.choice(valid_actions)
                else:
                    action = self.predict(state_now)

                # 实施action
                state_next, reward, game_status = self.my_maze.act(action, self.my_maze.get_current_state_simple)

                if (state, action) not in self.Q_table.keys():  # ensure value exists for (state, action) to avoid a KeyError
                    self.Q_table[(state, action)] = 0.0

                max_next_Q = max([self.Q_table.get((state_next, a), 0.0) for a in ACTIONS])
                self.Q_table[(state, action)] += self.learning_rate * (reward + self.gamma * max_next_Q - self.Q_table[(state, action)])

                if game_status == 'win':
                    win_history.append(1)
                    game_over = True
                elif game_status == 'lose':
                    win_history.append(0)
                    game_over = True
                else:
                    game_over = False

                state = state_next

                n_episodes += 1

            if len(win_history) > self.hsize:
                win_rate = sum(win_history[-self.hsize:]) / self.hsize

            template = "Epoch: {:03d}/{:d}    Episodes: {:d}  Win count: {:d} Win rate: {:.3f}"
            print(template.format(epoch, epoch_N-1, n_episodes, sum(win_history), win_rate))
            if type(output_line)!=type(None) and type(main_ui)!=type(None):
                output_line.setText(template.format(epoch, epoch_N-1, n_episodes, sum(win_history), win_rate))
                if epoch%200==0:
                    main_ui.repaint()

            # Save trained model weights and architecture, this will be used by the visualization code
            '''h5file = save_file + ".h5"
            json_file = save_file + ".json"
            model.save_weights(h5file, overwrite=True)
            with open(json_file, "w") as outfile:
                json.dump(model.to_json(), outfile)'''

            #测试是否训练成熟
            if win_rate > 0.9: self.epsilon_ = 0.05
            if self.my_maze.period == 0:
                if sum(win_history[-self.hsize:]) == self.hsize and self.completion_check():
                    print("Reached 100%% win rate at epoch: %d" % (epoch,))
                    break
            else:
                if win_rate>0.8 and self.play_game((0,0), 0):
                #if sum(win_history[-self.hsize:]) == self.hsize and self.play_game((0, 0), 0):
                    print("Reached 100%% win rate at epoch: %d" % (epoch,))
                    break

    def completion_check(self):
        if self.my_maze.period==0:
            period_temp = 1
        else:
            period_temp = self.my_maze.period
        for time_  in range(period_temp):
            for cell in self.my_maze.free_cells:
                if not self.my_maze.valid_actions(cell):
                    return False
                if not self.play_game(cell, time_):
                    return False
        return True

    def play_game(self, rat_cell, time):
        self.my_maze.reset(rat_cell, time)
        envstate = self.my_maze.get_current_state_simple()
        while True:
            prev_envstate = envstate
            # get next action
            action = self.predict(prev_envstate)

            # apply action, get rewards and new state
            envstate, reward, game_status = self.my_maze.act(action, self.my_maze.get_current_state_simple)
            if game_status == 'win':
                return True
            elif game_status == 'lose':
                return False

    def save_table(self, filename):
        #with open(filename,'w') as json_file:
         #   json.dump(self.Q_table, json_file, ensure_ascii=False)
        np.save(filename, self.Q_table)

    def load_table(self, filename):
        self.Q_table = np.load(filename).item()
        return self.Q_table

if __name__=="__main__":
    maze_name = 'maze10_3'
    maze = np.array(Mazes[maze_name])

    my_maze = Maze(maze_map=maze, period=2)
    model = QTableModel(my_maze)
    model.train()
    model.save_table("saved_qtable/"+maze_name)
    #model.load_table('saved_qtable/'+maze_name+'.npy')

    model.play_game((0,0), 0)
    draw_table_root_byTime(model, model.my_maze, (0,0))
    plt.show()
    print()