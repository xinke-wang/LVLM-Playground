import json
import os.path as osp
import re

import numpy as np


class Metric:
    MATRIX_CONFIG = {
        'tictactoe': {
            'size': 3,
            'count': 9,
            'valid_range': [-1, 0, 1]
        },
        'sudoku': {
            'size': 9,
            'count': 81,
            'valid_range': list(range(10))
        },
        'chess': {
            'size': 8,
            'count': 64,
            'valid_range': list(range(-6, 7))
        },
        'gomoku': {
            'size': 15,
            'count': 225,
            'valid_range': [0, 1, 2]
        },
        'minesweeper': {
            'size': 8,
            'count': 64,
            'valid_range': [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        },
        'reversi': {
            'size': 8,
            'count': 64,
            'valid_range': [0, 1, 2]
        }
    }

    RULE_FORMATS = {
        'tictactoe': r'(?:Movement:\s*)?([A-Ca-c][1-3]|[1-3][A-Ca-c])',
        'sudoku': r'(?:Movement:\s*)?([A-Ia-i][1-9]\s[1-9])',
        'chess':
        r'(?:Movement:\s*)?([a-hA-H][1-8][a-hA-H][1-8]|[a-hA-H][1-8]|O-O|O-O-O|(?:N|B|R|Q|K)?[a-hA-H]?[1-8]?x?[a-hA-H][1-8](?:=[QRNB])?|(?:N|B|R|Q|K)[a-hA-H][1-8])',  # noqa
        'gomoku':
        r'(?:Movement:\s*)?([A-Oa-o](?:[1-9]|1[0-5])|(?:[1-9]|1[0-5])[A-Oa-o])',  # noqa
        'minesweeper': r'(?:Movement:\s*)?([A-Ha-h][1-8]|[1-8][A-Ha-h])',
        'reversi': r'(?:Movement:\s*)?([A-Ha-h][1-8]|[1-8][A-Ha-h])'
    }

    TASK_ABILITIES = {
        'perceive': ['Perception'],
        'qa': ['Perception', 'Reasoning'],
        'rule': ['Perception', 'Reasoning', 'Decision'],
        'e2e': ['Perception', 'Reasoning', 'Decision', 'Adversary']
    }

    GAME_RATINGS = {
        'tictactoe': {
            'Perception': 0.5,
            'Reasoning': 0.5,
            'Decision': 0.5,
            'Adversary': 0.5
        },
        'reversi': {
            'Perception': 1.5,
            'Reasoning': 1.5,
            'Decision': 2.5,
            'Adversary': 2.5
        },
        'sudoku': {
            'Perception': 3.5,
            'Reasoning': 2.0,
            'Decision': 2.0,
            'Adversary': 0
        },
        'minesweeper': {
            'Perception': 4.0,
            'Reasoning': 5.0,
            'Decision': 3.0,
            'Adversary': 0
        },
        'gomoku': {
            'Perception': 5.0,
            'Reasoning': 4.0,
            'Decision': 3.5,
            'Adversary': 4.0
        },
        'chess': {
            'Perception': 3.5,
            'Reasoning': 3.0,
            'Decision': 5.0,
            'Adversary': 5.0
        }
    }

    def __init__(self, record_path, annotation_dir):
        self.record_path = record_path
        self.annotation_dir = annotation_dir
        with open(self.record_path, 'r') as f:
            self.record = json.load(f)
        self.debug_results = {}
        self.scores = {}
        self.weighted_summary = {}

    def parse_perceive(self, lmm_output, game_name):
        match = re.search(r'(?:Game State:\s*)?(?:(\[\[.*\]\])|```(.*?)```)',
                          lmm_output, re.DOTALL)
        if not match:
            return None, "No valid matrix or 'Game State:' found"

        matrix_str = match.group(1) if match.group(1) else match.group(
            2).strip()

        matrix_match = re.search(r'\[\[.*\]\]', matrix_str, re.DOTALL)
        if not matrix_match:
            return None, 'Matrix format not matched'
        matrix_content = matrix_match.group(0)

        numbers = re.findall(r'-?\d+', matrix_content)
        config = self.MATRIX_CONFIG.get(game_name)
        if not config or len(numbers) != config['count']:
            return None, f"Number count mismatch: expected {config['count']}, got {len(numbers)}"  # noqa

        try:
            matrix_flat = [int(num) for num in numbers]
            if not all(num in config['valid_range'] for num in matrix_flat):
                return None, f"Numbers out of range {config['valid_range']}"
            matrix = [
                matrix_flat[i:i + config['size']]
                for i in range(0, config['count'], config['size'])
            ]
            return matrix, None
        except ValueError as e:
            return None, f'Conversion error: {e}'

    def parse_rule(self, lmm_output, game_name):
        if lmm_output is None:
            return None, 'No valid output found.'
        pattern = self.RULE_FORMATS.get(game_name)
        if not pattern:
            return None, 'No pattern defined for this game'
        match = re.search(pattern, lmm_output, re.IGNORECASE)
        if match:
            move = match.group(1)
            if game_name in ['tictactoe', 'gomoku', 'minesweeper', 'reversi'
                             ] and move[0].isdigit():
                move = move[1:] + move[0]
            return move.upper(), None
        return None, 'Move format not matched'

    def parse_qa(self, lmm_output, _):
        if lmm_output is None:
            return None, 'No valid output found.'
        patterns = [
            r'(?:Final\s+Answer[:\s]*(?:\\boxed{)?\s*)([A-Da-d])(?:\s*})?',
            r'Answer[:\s]+([A-Da-d])(?:\s*\d)?', r'\[([A-Da-d])\]'
        ]
        for pattern in patterns:
            match = re.search(pattern, lmm_output, re.IGNORECASE)
            if match:
                return match.group(1).upper(), None

        match = re.search(r'([A-Da-d])(?:\s*\]|\.|$|\s)', lmm_output,
                          re.IGNORECASE)
        if match:
            return match.group(1).upper(), None

        return None, 'Answer format not matched (expected [A-D])'

    def evaluate_perceive(self, game_name, annotation):
        results = self.record['perceive'][game_name]
        accuracies = []
        debug_data = []
        for i, result in enumerate(results):
            if result is None or 'raw' not in result:
                debug_data.append({
                    'index': i,
                    'raw': None,
                    'parsed': None,
                    'reason': 'No raw output provided'
                })
                accuracies.append(0)
                continue
            lmm_output = result['raw']
            gt = annotation['annotations'][i]['gt']
            parsed_matrix, reason = self.parse_perceive(lmm_output, game_name)
            entry = {'index': i, 'raw': lmm_output, 'parsed': parsed_matrix}
            if reason:
                entry['reason'] = reason
            debug_data.append(entry)
            if parsed_matrix is None:
                accuracies.append(0)
            else:
                gt_np = np.array(gt)
                matrix_np = np.array(parsed_matrix)
                accuracy = np.sum(gt_np == matrix_np) / gt_np.size
                accuracies.append(accuracy)
        if 'perceive' not in self.debug_results:
            self.debug_results['perceive'] = {}
        self.debug_results['perceive'][game_name] = debug_data
        avg_score = round(sum(accuracies) /
                          len(accuracies), 3) if accuracies else 0
        if 'perceive' not in self.scores:
            self.scores['perceive'] = {}
        self.scores['perceive'][game_name] = avg_score
        return avg_score

    def evaluate_qa(self, game_name, annotation):
        results = self.record['qa'][game_name]
        accuracies = []
        debug_data = []
        for i, result in enumerate(results):
            if result is None or 'raw' not in result:
                debug_data.append({
                    'index': i,
                    'raw': None,
                    'parsed': None,
                    'reason': 'No raw output provided'
                })
                accuracies.append(0)
                continue
            lmm_output = result['raw']
            gt = annotation['annotations'][i]['gt']['answer']
            parsed_answer, reason = self.parse_qa(lmm_output, game_name)
            entry = {'index': i, 'raw': lmm_output, 'parsed': parsed_answer}
            if reason:
                entry['reason'] = reason
            debug_data.append(entry)
            accuracy = 1 if parsed_answer == gt else 0
            accuracies.append(accuracy)
        if 'qa' not in self.debug_results:
            self.debug_results['qa'] = {}
        self.debug_results['qa'][game_name] = debug_data
        avg_score = round(sum(accuracies) /
                          len(accuracies), 3) if accuracies else 0
        if 'qa' not in self.scores:
            self.scores['qa'] = {}
        self.scores['qa'][game_name] = avg_score
        return avg_score

    def evaluate_rule(self, game_name, annotation):
        results = self.record['rule'][game_name]
        accuracies = []
        debug_data = []
        for i, result in enumerate(results):
            if result is None or 'raw' not in result:
                debug_data.append({
                    'index': i,
                    'raw': None,
                    'parsed': None,
                    'reason': 'No raw output provided'
                })
                accuracies.append(0)
                continue
            lmm_output = result['raw']
            valid_movements = annotation['annotations'][i]['gt'][
                'valid_movements']
            parsed_move, reason = self.parse_rule(lmm_output, game_name)
            entry = {'index': i, 'raw': lmm_output, 'parsed': parsed_move}
            if reason:
                entry['reason'] = reason
            debug_data.append(entry)
            if parsed_move:
                normalized_move = parsed_move.lower()
                normalized_valid_movements = [
                    move.lower() for move in valid_movements
                ]
                accuracy = 1 if normalized_move in normalized_valid_movements else 0  # noqa
            else:
                accuracy = 0
            accuracies.append(accuracy)
        if 'rule' not in self.debug_results:
            self.debug_results['rule'] = {}
        self.debug_results['rule'][game_name] = debug_data
        avg_score = round(sum(accuracies) /
                          len(accuracies), 3) if accuracies else 0
        if 'rule' not in self.scores:
            self.scores['rule'] = {}
        self.scores['rule'][game_name] = avg_score
        return avg_score

    def evaluate_e2e(self, game_name):
        results = self.record['e2e'][game_name]
        scores = []
        debug_data = []
        for i, result in enumerate(results):
            if result is None or not isinstance(result,
                                                dict) or 'score' not in result:
                debug_data.append({
                    'index':
                    i,
                    'parsed':
                    None,
                    'reason':
                    f'Invalid e2e data format: {result}'
                })
                scores.append(0)
            else:
                debug_data.append({
                    'index': i,
                    'parsed': {
                        'score': result['score'],
                        'steps': result.get('steps', 0)
                    }
                })
                scores.append(result['score'])
        if 'e2e' not in self.debug_results:
            self.debug_results['e2e'] = {}
        self.debug_results['e2e'][game_name] = debug_data
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0
        if 'e2e' not in self.scores:
            self.scores['e2e'] = {}
        self.scores['e2e'][game_name] = avg_score
        return avg_score

    def evaluate_all(self):
        if self.scores and self.weighted_summary:
            return self.scores

        self.weighted_summary = {}

        for task in self.record:
            total_weighted_score = 0
            total_weight = 0

            for game in self.record[task]:
                annotation_path = osp.join(self.annotation_dir, task, game,
                                           'annotation.json')
                if task != 'e2e' and osp.exists(annotation_path):
                    with open(annotation_path, 'r') as f:
                        annotation = json.load(f)
                else:
                    annotation = None

                if task == 'perceive':
                    avg_score = self.evaluate_perceive(game, annotation)
                elif task == 'qa':
                    avg_score = self.evaluate_qa(game, annotation)
                elif task == 'rule':
                    avg_score = self.evaluate_rule(game, annotation)
                elif task == 'e2e':
                    avg_score = self.evaluate_e2e(game)

                game_ratings = self.GAME_RATINGS.get(game.lower(), {})
                task_abilities = self.TASK_ABILITIES.get(task, [])
                weight = sum(
                    game_ratings.get(ability, 0) for ability in task_abilities)
                weighted_score = avg_score * weight
                total_weighted_score += weighted_score
                total_weight += weight if weight > 0 else 1

            weighted_avg_score = round(total_weighted_score / total_weight,
                                       3) if total_weight > 0 else 0
            self.weighted_summary[task] = {
                'weighted_average': weighted_avg_score
            }

        return self.scores

    def save_evaluation(self, output_path):
        self.evaluate_all()
        result = {
            'weighted_summary': self.weighted_summary,
            'scores': self.scores,
            'details': self.debug_results,
        }
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=4)
