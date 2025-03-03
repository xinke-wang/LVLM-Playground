import gc
import json
import os
import os.path as osp

import torch
from pjtools.configurator import AutoConfigurator

from playground.evaluator import Evaluator
from playground.registry import AGENT_REGISTRY
from playground.state_code import GameStatusEncoder


class Recipe:

    def __init__(self, args):
        self.base_cfg = AutoConfigurator.fromfile('configs/base.py')
        self.recipe = AutoConfigurator.fromfile(args.exp_recipe)
        self.agent_cfg = AutoConfigurator.fromfile(args.agent_cfg)
        self.agent_cfg_path = args.agent_cfg
        self.benchmark_setting = self.base_cfg.benchmark_setting

        self.save_path = osp.join(self.recipe.save_path, self.recipe.name)
        os.makedirs(self.save_path, exist_ok=True)
        self.log_file = osp.join(self.save_path, 'evaluation.log')

        self.agent = AGENT_REGISTRY.get(self.agent_cfg.lmm_agent.agent)(
            self.agent_cfg)

        self.init_experiment_record()

    def init_experiment_record(self):
        self.record_path = osp.join(
            self.save_path,
            self.agent_cfg.lmm_agent.name + self.recipe.name + '.json')
        if osp.exists(self.record_path):
            with open(self.record_path, 'r') as f:
                self.record = json.load(f)
        else:
            self.record = {}

        self.update_record_with_new_tasks_and_games()
        self.save_record()

    def update_record_with_new_tasks_and_games(self):
        tasks = self.recipe.tasks
        games = self.recipe.games
        sample_size = self.benchmark_setting.sample_size
        e2e_round = self.benchmark_setting.e2e_round

        for task in tasks:
            if task not in self.record:
                self.record[task] = {}
            repetition_round = sample_size if task != 'e2e' else e2e_round
            for game in games:
                if game not in self.record[task]:
                    self.record[task][game] = [None] * repetition_round

    def save_record(self):
        with open(self.record_path, 'w') as f:
            json.dump(self.record, f, indent=4, cls=GameStatusEncoder)

    def run_experiments(self):
        tasks = self.recipe.tasks
        games = self.recipe.games

        for task in tasks:
            for game in games:
                if task not in self.record:
                    self.record[task] = {}
                if game not in self.record[task]:
                    self.record[task][game] = [None
                                               ] * self.recipe.repetition_round
                    self.save_record()

                if task != 'e2e':
                    with open(osp.join(self.benchmark_setting.benchmark_path,
                                       task, game, 'annotation.json'),
                              'r',
                              encoding='utf-8') as json_file:
                        annotation = json.load(json_file)
                    assert annotation['game'] == game
                    assert annotation['task'] == task
                    assert len(annotation['annotations']
                               ) == self.benchmark_setting.sample_size

                completed_rounds = self.record[task][game]

                game_cfg = AutoConfigurator.fromfile(
                    f'configs/games/{game}.py')

                evaluator = Evaluator(game_cfg, self.agent, task,
                                      self.log_file, self.save_path)

                while None in completed_rounds:
                    next_round = completed_rounds.index(None)

                    print(f'Running experiment for task: {task}, '
                          f'game: {game}, round: {next_round + 1}')

                    try:
                        if task != 'e2e':
                            batch = {
                                'task':
                                task,
                                'screenshot_path':
                                osp.join(self.benchmark_setting.benchmark_path,
                                         task, game, f'{next_round:07d}.jpg'),
                                'gt':
                                annotation['annotations'][next_round]['gt'],
                                'game_cfg':
                                game_cfg
                            }
                        else:
                            batch = {'task': task, 'game_cfg': game_cfg}
                        result, simulator = evaluator.run(batch)
                        simulator.cleanup()
                        self.record[task][game][next_round] = result
                        self.save_record()
                        completed_rounds = self.record[task][game]
                    except Exception as e:
                        print(
                            f'Error occurred during task {task}, game {game}, '
                            f'round {next_round + 1}: {e}')
                        continue

                print(f'Task: {task}, game: {game} has been completed.')

                torch.cuda.synchronize()
                evaluator.cleanup()
                del evaluator
                torch.cuda.empty_cache()
                gc.collect()

    def cleanup(self):
        """Clean up resources at the end of the experiment."""
        if hasattr(self.agent, 'model'):
            del self.agent.model
        del self.agent
        torch.cuda.empty_cache()
        gc.collect()
