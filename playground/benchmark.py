import json
import os
import os.path as osp
import sys

from pjtools.configurator import AutoConfigurator
from PyQt5.QtWidgets import QApplication

from playground.registry import GAME_REGISTRY
from playground.utils import set_random_seed


class Generator:

    def __init__(self, base_cfg):
        cfg = AutoConfigurator.fromfile(base_cfg)
        self.benchmark_setting = cfg.benchmark_setting
        self.seed = set_random_seed()
        self.sample_size = self.benchmark_setting.sample_size

    def generate_benchmark(self):
        for task in self.benchmark_setting.offline_task:
            for game in self.benchmark_setting.games:
                save_path = osp.join(self.benchmark_setting.benchmark_path,
                                     task, game)
                if not osp.exists(save_path):
                    os.makedirs(save_path)
                if osp.exists(osp.join(save_path, 'annotation.json')):
                    print(
                        f'Benchmark data for {task} in {game} has been found.')
                else:
                    self.render(task, game, save_path)

    def render(self, task, game, save_path):
        game_cfg = AutoConfigurator.fromfile(f'configs/games/{game}.py')
        app = QApplication(sys.argv)  # noqa
        if task == 'perceive':
            self.render_perceive(game_cfg, save_path)
        elif task == 'rule':
            self.render_rule(game_cfg, save_path)
        elif task == 'qa':
            self.render_qa(game_cfg, save_path)
        else:
            raise ValueError(f'Invalid task: {task}')

    def render_perceive(self, game_cfg, save_path):
        game_class = GAME_REGISTRY.get(game_cfg.game_name)
        annotations = []
        for i in range(self.sample_size):
            game = game_class(game_cfg)
            gt = game.get_random_state()
            screenshot = game.get_screenshot()
            screenshot.save(osp.join(save_path, f'{i:07d}.jpg'))
            annotation = {
                'file': f'{i:07d}.jpg',
                'gt': gt,
            }
            annotations.append(annotation)
        with open(osp.join(save_path, 'annotation.json'),
                  'w',
                  encoding='utf-8') as json_file:
            json.dump(
                {
                    'task': 'perceive',
                    'game': game_cfg.game_name,
                    'annotations': annotations,
                }, json_file)

    def render_qa(self, game_cfg, save_path):
        game_class = GAME_REGISTRY.get(game_cfg.game_name)
        annotations = []
        for i in range(self.sample_size):
            game = game_class(game_cfg)
            random_state = game.get_random_state()
            QA = game_cfg.qa(game_cfg.game_description['qa'])
            qa_pairs = QA.get_qa_pairs(random_state)
            example_qa = '\n'.join(f'Question: {q}\nAnswer: {a}'
                                   for q, a in qa_pairs[:QA.shot])
            question, answer = qa_pairs[QA.shot]
            screenshot = game.get_screenshot()
            screenshot.save(osp.join(save_path, f'{i:07d}.jpg'))
            annotation = {
                'file': f'{i:07d}.jpg',
                'gt': {
                    'question': question,
                    'answer': answer,
                    'example_qa': example_qa
                },
            }
            annotations.append(annotation)
        with open(osp.join(save_path, 'annotation.json'),
                  'w',
                  encoding='utf-8') as json_file:
            json.dump(
                {
                    'task': 'qa',
                    'game': game_cfg.game_name,
                    'annotations': annotations,
                }, json_file)

    def render_rule(self, game_cfg, save_path):
        game_class = GAME_REGISTRY.get(game_cfg.game_name)
        annotations = []
        for i in range(self.sample_size):
            game = game_class(game_cfg)
            rule_state, valid_movements = game.get_rule_state()
            screenshot = game.get_screenshot()
            screenshot.save(osp.join(save_path, f'{i:07d}.jpg'))
            annotation = {
                'file': f'{i:07d}.jpg',
                'gt': {
                    'rule_state': rule_state,
                    'valid_movements': valid_movements
                },
            }
            annotations.append(annotation)
        with open(osp.join(save_path, 'annotation.json'),
                  'w',
                  encoding='utf-8') as json_file:
            json.dump(
                {
                    'task': 'rule',
                    'game': game_cfg.game_name,
                    'annotations': annotations,
                }, json_file)
