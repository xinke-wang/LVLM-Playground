import os.path as osp
import time

import torch

from playground.simulator import GameSimulator
from playground.utils import set_random_seed


class Evaluator:
    """Evaluator class to run the game with the given agent."""

    def __init__(self, game_cfg, agent, task, log_file, save_path):
        self.game_cfg = game_cfg
        self.agent = agent
        self.task = task
        self.save_path = osp.join(save_path, self.game_cfg.game_name,
                                  self.task,
                                  self.agent.agent_cfg.lmm_agent.name)
        self.seed = set_random_seed()
        self.log_file = log_file

    def run(self, batch):
        if self.task == 'e2e':
            return self.run_e2e_game(batch)
        elif self.task == 'perceive':
            return self.run_perceive(batch)
        elif self.task == 'rule':
            return self.run_rule(batch)
        elif self.task == 'qa':
            return self.run_qa(batch)
        else:
            raise ValueError(f'Invalid task type: {self.task}')

    def run_e2e_game(self, batch):
        crt_save_path = osp.join(self.save_path, f'round_{int(time.time())}')
        simulator = GameSimulator(self.game_cfg, self.agent, self.seed,
                                  crt_save_path, self.task)

        result = simulator.run_e2e(batch)

        # if self.game_cfg.make_video:
        #     simulator.make_video()

        return result, simulator

    def run_perceive(self, batch):
        crt_save_path = osp.join(self.save_path)
        simulator = GameSimulator(self.game_cfg,
                                  self.agent,
                                  self.seed,
                                  crt_save_path,
                                  self.task,
                                  log_file=self.log_file)
        result = simulator.perceive(batch)

        return result, simulator

    def run_rule(self, batch):
        crt_save_path = osp.join(self.save_path)
        simulator = GameSimulator(self.game_cfg,
                                  self.agent,
                                  self.seed,
                                  crt_save_path,
                                  self.task,
                                  log_file=self.log_file)
        result = simulator.rule(batch)

        return result, simulator

    def run_qa(self, batch):
        crt_save_path = osp.join(self.save_path)
        simulator = GameSimulator(self.game_cfg,
                                  self.agent,
                                  self.seed,
                                  crt_save_path,
                                  self.task,
                                  log_file=self.log_file)
        result = simulator.qa(batch)

        return result, simulator

    def cleanup(self):
        torch.cuda.empty_cache()
