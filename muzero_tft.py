import torch
import torch.nn as nn
import torch.optim as optim
from collections import namedtuple
import random

from tft_alias import TFTAliasEnv

# Environment factory
# Uses a simplified TFT alias environment defined in tft_alias.py
def make_env():
    return TFTAliasEnv()

# MuZero network components
class RepresentationNetwork(nn.Module):
    def __init__(self, obs_dim, hidden_dim):
        super().__init__()
        self.fc = nn.Linear(obs_dim, hidden_dim)

    def forward(self, x):
        return torch.tanh(self.fc(x))

class DynamicsNetwork(nn.Module):
    def __init__(self, hidden_dim, action_dim):
        super().__init__()
        self.fc_action = nn.Linear(action_dim, hidden_dim)
        self.fc_hidden = nn.Linear(hidden_dim, hidden_dim)
        self.reward_head = nn.Linear(hidden_dim, 1)

    def forward(self, hidden, action_one_hot):
        x = torch.tanh(self.fc_hidden(hidden) + self.fc_action(action_one_hot))
        reward = self.reward_head(x)
        return x, reward

class PredictionNetwork(nn.Module):
    def __init__(self, hidden_dim, action_dim):
        super().__init__()
        self.policy_head = nn.Linear(hidden_dim, action_dim)
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, hidden):
        policy_logits = self.policy_head(hidden)
        value = self.value_head(hidden)
        return policy_logits, value

class MuZeroNet(nn.Module):
    def __init__(self, obs_dim, hidden_dim, action_dim):
        super().__init__()
        self.representation = RepresentationNetwork(obs_dim, hidden_dim)
        self.dynamics = DynamicsNetwork(hidden_dim, action_dim)
        self.prediction = PredictionNetwork(hidden_dim, action_dim)
        self.action_dim = action_dim

    def initial_inference(self, obs):
        hidden = self.representation(obs)
        policy_logits, value = self.prediction(hidden)
        reward = torch.zeros(1)
        return hidden, policy_logits, value, reward

    def recurrent_inference(self, hidden, action):
        action_one_hot = torch.nn.functional.one_hot(action, num_classes=self.action_dim).float()
        next_hidden, reward = self.dynamics(hidden, action_one_hot)
        policy_logits, value = self.prediction(next_hidden)
        return next_hidden, policy_logits, value, reward

# Storage for experience (simplified)
Transition = namedtuple('Transition', 'obs action reward next_obs done')

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = []
        self.capacity = capacity

    def push(self, *args):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

# Simplified training loop skeleton
class MuZeroAgent:
    def __init__(self, obs_dim, action_dim, hidden_dim=128, lr=1e-3):
        self.net = MuZeroNet(obs_dim, hidden_dim, action_dim)
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr)
        self.replay_buffer = ReplayBuffer()
        self.batch_size = 32

    def select_action(self, obs):
        with torch.no_grad():
            _, policy_logits, _, _ = self.net.initial_inference(obs)
            action = torch.distributions.Categorical(logits=policy_logits).sample()
        return action.item()

    def store_transition(self, obs, action, reward, next_obs, done):
        self.replay_buffer.push(obs, action, reward, next_obs, done)

    def update(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        transitions = self.replay_buffer.sample(self.batch_size)
        batch = Transition(*zip(*transitions))
        obs_batch = torch.stack(batch.obs)
        action_batch = torch.tensor(batch.action)
        reward_batch = torch.tensor(batch.reward)
        next_obs_batch = torch.stack(batch.next_obs)
        done_batch = torch.tensor(batch.done, dtype=torch.float32)

        hidden, policy_logits, value, reward_pred = self.net.initial_inference(obs_batch)
        value_target = reward_batch + (1 - done_batch) * 0.99  # bootstrap with discount

        policy_loss = nn.functional.cross_entropy(policy_logits, action_batch)
        value_loss = nn.functional.mse_loss(value.squeeze(), value_target)
        reward_loss = nn.functional.mse_loss(reward_pred.squeeze(), reward_batch)
        loss = policy_loss + value_loss + reward_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

def train(num_episodes=10):
    env = make_env()
    agent = MuZeroAgent(obs_dim=env.observation_space.numel(), action_dim=env.action_space)

    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0
        while not done:
            action = agent.select_action(obs)
            next_obs, reward, done, _ = env.step(action)
            agent.store_transition(obs, action, reward, next_obs, done)
            loss = agent.update()
            obs = next_obs
            episode_reward += reward
        print(f"Episode {episode}: reward {episode_reward:.2f}")

if __name__ == "__main__":
    train()
