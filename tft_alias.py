import random
import torch

class TFTAliasEnv:
    """A simplified Teamfight Tactics environment."""
    def __init__(self, board_size=3, shop_size=3, unit_types=5, max_turns=20):
        self.board_size = board_size
        self.shop_size = shop_size
        self.unit_types = unit_types
        self.max_turns = max_turns
        self.action_space = 4  # buy, reroll, sell, end turn
        obs_len = board_size + shop_size + 1  # board + shop + gold
        self.observation_space = torch.zeros(obs_len)
        self.reset()

    def reset(self):
        self.turns = 0
        self.gold = 10
        self.board = [-1] * self.board_size
        self.shop = [self._random_unit() for _ in range(self.shop_size)]
        return self._get_obs()

    def _random_unit(self):
        return random.randint(0, self.unit_types - 1)

    def _get_obs(self):
        board = [u if u >= 0 else self.unit_types for u in self.board]
        obs = board + self.shop + [self.gold]
        return torch.tensor(obs, dtype=torch.float32)

    def _synergy_reward(self):
        counts = {}
        for u in self.board:
            if u >= 0:
                counts[u] = counts.get(u, 0) + 1
        return float(sum(c * c for c in counts.values()))

    def step(self, action):
        reward = 0.0
        if action == 0:  # buy first shop unit
            if self.gold >= 2 and -1 in self.board:
                slot = self.board.index(-1)
                self.board[slot] = self.shop[0]
                self.gold -= 2
                self.shop[0] = self._random_unit()
        elif action == 1:  # reroll shop
            if self.gold >= 1:
                self.gold -= 1
                self.shop = [self._random_unit() for _ in range(self.shop_size)]
        elif action == 2:  # sell first board unit
            if self.board[0] != -1:
                self.gold += 1
                self.board[0] = -1
        elif action == 3:  # end turn and gain reward based on synergies
            reward = self._synergy_reward()
            self.gold += 5
        self.turns += 1
        done = self.turns >= self.max_turns
        obs = self._get_obs()
        return obs, reward, done, {}
