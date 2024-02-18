#using the ready-made cart-pole, but this one is more realistic
import gym
import numpy as np
import time
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

#second reason for using a pre-written cartpole, pretty display
env = gym.make('CartPole-v1')

State = tuple[int, int, int, int]
Cont_State = tuple[float, float, float, float]
class Agent():
    def __init__(self, alpha=0.5, epsilon=0.05, gamma=1):
        self.Q = {}
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.buckets = [3, 3, 6, 6]
        self.obs_mins = [-2.4, -3, -0.210, -3]
        self.obs_maxs = [2.4, 3, 0.210, 3]
        self.a_space = env.action_space.n


    def update_Q \
    (self, s: State, a: int, next_s: State, r: int): 
        if s not in self.Q:
            self.Q[s] = [np.random.rand() for _ in range(self.a_space)]
        if next_s not in self.Q:
            self.Q[next_s] = [np.random.rand() for _ in range(self.a_space)]
        delta_q = (r + self.gamma * max(self.Q[next_s]) - self.Q[s][a])
        delta_q *= self.alpha
        self.Q[s][a] += delta_q

    def get_action \
    (self, state: State) -> int:
        if state not in self.Q or np.random.rand() < self.epsilon:
            return np.random.randint(0, env.action_space.n)
        return np.argmax(self.Q[state])

    def discretize_state \
    (self, state: Cont_State) -> State:
        ret = [0 for _ in range(len(state))]
        #normalize state, multiply it so that i get an index
        for i in range(len(ret)):
            v_min = self.obs_mins[i]
            v_max = self.obs_maxs[i]
            ret[i] = (state[i] - v_min) / (v_max - v_min) 
            ret[i] = int(round(ret[i] * self.buckets[i]))
        return tuple(ret)
    


steps_log = []
moving_averages = []
agent = Agent()
for _ in range(1000):
    #cont state
    cstate, _ = env.reset()
    s = agent.discretize_state(cstate.tolist())
    term = False
    truncated = False
    steps = 0
    while not term and not truncated:
        a = agent.get_action(s)
        cstate, r, term, truncated, _ = env.step(a)
        if term and steps < 200:
            r = -475
        next_s = agent.discretize_state(cstate.tolist())
        agent.update_Q(s, a, next_s, r)
        s = next_s
        steps += 1
    steps_log.append(steps)
    moving_averages.append(np.mean(steps_log))

plt.plot(steps_log)
#pretty line
plt.plot(moving_averages)
plt.show()
