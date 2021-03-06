import pickle

import gym
import numpy as np
import pyswarms as ps
from gym.wrappers import TimeLimit

from fuzzy_system import FuzzySystem

np.seterr(divide='ignore', invalid='ignore')
gym.logger.set_level(40)
number_of_rules = 2
discount_factor = 0.97
number_of_episodes = 100
horizon = 200
env: TimeLimit = gym.make('CartPole-v0')
env.seed()
dimension = env.observation_space.shape[0]

randoms = np.random.randint(low=0, high=number_of_episodes, size=number_of_episodes)


def run_episode(rand, fuzzy_system: FuzzySystem):
    env.seed(int(rand))
    observation = env.reset()
    total_reward = 0
    for i in range(horizon):
        action = fuzzy_system.take_action(observation)
        action = int(action > 0)
        observation, reward, done, info = env.step(action)
        # make it -1 instead of 1
        reward = -reward
        total_reward += (reward * (discount_factor ** i))
        if done:
            break
    return total_reward


def particle_reward(params):
    fuzzy_system = FuzzySystem(params, number_of_rules, dimension)
    total_reward = 0
    for i in range(number_of_episodes):
        total_reward += run_episode(randoms[i], fuzzy_system)
    total_reward /= number_of_episodes
    return total_reward


def fitness(X):
    return np.array([particle_reward(X[i]) for i in range(X.shape[0])])


options = {'c1': 2.05, 'c2': 2.05, 'w': 0.729, "k": 30, 'p': 2}
optimizer = ps.single.LocalBestPSO(n_particles=100, dimensions=(2 * dimension + 1) * number_of_rules + 1,
                                   options=options)
# optimizer = ps.single.GlobalBestPSO(n_particles=100, dimensions=(2 * dimension + 1) * number_of_rules + 1,
#                                     options=options)
print("begin training")
cost, pos = optimizer.optimize(fitness, print_step=1, iters=20, verbose=3)
with open("result.pkl", "wb") as f:
    pickle.dump({"cost": cost, "best": pos, "dimension": dimension, "number_of_rules": number_of_rules}, f)
env.close()
