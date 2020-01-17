import numpy as np

NUM_ACTION = 4

#存储episode
class Git(object):
    def __init__(self, model, max_save_size, gamma=0.9):
        self.model = model
        self.max_save_size = max_save_size
        self.gamma = gamma
        self.memory = list()

    def remember(self, episode):
        # episode: [state_now, action, reward, state_next, game_over]
        self.memory.append(episode)
        if len(self.memory) > self.max_save_size:
            del self.memory[0]

    def predict(self, state_now):
        return self.model.predict(state_now)[0]

    def get_data(self, batch_size=10):
        state_size = self.memory[0][0].shape[1]  # 地图上的格子数
        mem_sum = len(self.memory)
        batch_size = min(mem_sum, batch_size)
        inputs = np.zeros((batch_size, state_size))
        targets = np.zeros((batch_size, NUM_ACTION))
        for i, index in enumerate(np.random.choice(range(mem_sum), batch_size, replace=False)):
            state_now, action, reward, state_next, game_over = self.memory[index]
            inputs[i] = state_now
            if game_over:
                targets[i, action] = reward
            else:
                Q_sa = np.max(self.predict(state_next)) # Q_sa 贪心算法
                targets[i, action] = reward + self.gamma * Q_sa
        return inputs, targets
