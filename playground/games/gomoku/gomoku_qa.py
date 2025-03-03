import random
import re
from typing import Dict, Tuple

from playground.evaluator.base_qa import BaseQuestionAnswering


class GomokuQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_symbol_at_position_question,
            self._generate_count_stones_question,
            self._generate_row_column_count_question,
            self._generate_winning_condition_question,
            self._generate_adjacent_stones_question,
            self._generate_empty_cells_question,
            self._generate_max_consecutive_stones_question,
            self._generate_edge_stones_count_question,
        ]
        self.rows = 'ABCDEFGHIJKLMNO'
        self._last_correct_answer = None
        self._last_options = None

    def _generate_mc_options(self, correct_answer: str,
                             question_type: str) -> Tuple[Dict[str, str], str]:
        possible_options = []

        if question_type == 'symbol':
            possible_options = ['Black', 'White', 'empty']
            if correct_answer not in possible_options:
                possible_options.append(correct_answer)

        elif question_type == 'count':
            correct_num = int(correct_answer)
            possible_range = list(
                range(max(0, correct_num - 3), correct_num + 4))
            possible_options = [
                str(num) for num in possible_range if num != correct_num
            ]
            random.shuffle(possible_options)
            possible_options = possible_options[:3]
            possible_options.append(str(correct_num))

        elif question_type == 'yes_no':
            possible_options = ['yes', 'no', 'maybe', 'unknown']
            if correct_answer not in possible_options:
                possible_options.append(correct_answer)

        possible_options = list(set(possible_options))
        if correct_answer in possible_options:
            possible_options.remove(correct_answer)
        random.shuffle(possible_options)

        unique_options = []
        seen = set()
        for opt in possible_options:
            if opt not in seen and len(unique_options) < 3:
                unique_options.append(opt)
                seen.add(opt)
        insert_position = random.randint(0, len(unique_options))
        unique_options.insert(insert_position, correct_answer)

        options = {}
        option_letters = ['A', 'B', 'C', 'D']
        for i, option in enumerate(unique_options):
            options[option_letters[i]] = option
        correct_letter = None
        for letter, value in options.items():
            if value == correct_answer:
                correct_letter = letter
                break

        return options, correct_letter

    def _format_mc_question(self, question: str, options: Dict[str,
                                                               str]) -> str:
        question = re.sub(r'Please respond with.*', '', question).strip()
        formatted_question = f'{question}\n'
        for letter, value in options.items():
            formatted_question += f'{letter}. {value}\n'
        return formatted_question.strip()

    def get_qa_pair(self, game_state):
        while True:
            question_func = random.choice(self.question_pool)
            question_text, raw_answer, question_type = question_func(
                game_state)
            options, correct_letter = self._generate_mc_options(
                str(raw_answer), question_type)
            self._last_correct_answer = correct_letter
            self._last_options = options
            formatted_question = self._format_mc_question(
                question_text, options)

            return formatted_question, correct_letter

    def get_answer(self, game_state, question):
        if self._last_correct_answer is not None and self._last_options is not None:  # noqa
            answer = self._last_correct_answer
            self._last_correct_answer = None
            self._last_options = None
            return answer
        else:
            return 'No stored multiple-choice answer.'

    def _generate_symbol_at_position_question(self, game_state):
        row_idx = random.randint(0, 14)
        col_idx = random.randint(0, 14)
        row_label = self.rows[row_idx]
        question_text = f'What is the stone at row {row_label}, column {col_idx}?'  # noqa
        raw_answer = self._get_symbol_at_position(game_state, row_idx, col_idx)
        return question_text, raw_answer, 'symbol'

    def _generate_count_stones_question(self, game_state):
        stone_color = random.choice(['Black', 'White'])
        question_text = f"How many '{stone_color}' stones are on the board?"  # noqa
        raw_answer = self._count_stones(game_state, stone_color)
        return question_text, raw_answer, 'count'

    def _generate_row_column_count_question(self, game_state):
        axis = random.choice(['row', 'column'])
        stone_color = random.choice(['Black', 'White'])
        if axis == 'row':
            row_idx = random.randint(0, 14)
            row_label = self.rows[row_idx]
            question_text = f"How many '{stone_color}' stones are in row {row_label}?"  # noqa
            raw_answer = self._count_stones_in_row(game_state, row_idx,
                                                   stone_color)
        else:
            col_idx = random.randint(0, 14)
            question_text = f"How many '{stone_color}' stones are in column {col_idx}?"  # noqa
            raw_answer = self._count_stones_in_column(game_state, col_idx,
                                                      stone_color)
        return question_text, raw_answer, 'count'

    def _generate_winning_condition_question(self, game_state):
        question_text = 'Is there a winning line on the board?'
        raw_answer = self._check_winning_condition(game_state)
        return question_text, raw_answer, 'yes_no'

    def _generate_adjacent_stones_question(self, game_state):
        row_idx = random.randint(0, 14)
        col_idx = random.randint(0, 14)
        row_label = self.rows[row_idx]
        question_text = f'How many stones are adjacent to row {row_label}, column {col_idx}?'  # noqa
        raw_answer = self._count_adjacent_stones(game_state, row_idx, col_idx)
        return question_text, raw_answer, 'count'

    def _generate_empty_cells_question(self, game_state):
        question_text = 'How many empty cells are there on the board?'
        raw_answer = self._count_empty_cells(game_state)
        return question_text, raw_answer, 'count'

    def _generate_max_consecutive_stones_question(self, game_state):
        axis = random.choice(['row', 'column', 'diagonal'])
        stone_color = random.choice(['Black', 'White'])
        if axis == 'row':
            row_idx = random.randint(0, 14)
            row_label = self.rows[row_idx]
            question_text = f"What is the maximum number of consecutive '{stone_color}' stones in row {row_label}?"  # noqa
            raw_answer = self._max_consecutive_in_row(game_state, row_idx,
                                                      stone_color)
        elif axis == 'column':
            col_idx = random.randint(0, 14)
            question_text = f"What is the maximum number of consecutive '{stone_color}' stones in column {col_idx}?"  # noqa
            raw_answer = self._max_consecutive_in_column(
                game_state, col_idx, stone_color)
        else:
            question_text = f"What is the maximum number of consecutive '{stone_color}' stones on any diagonal?"  # noqa
            raw_answer = self._max_consecutive_on_diagonal(
                game_state, stone_color)
        return question_text, raw_answer, 'count'

    def _generate_edge_stones_count_question(self, game_state):
        stone_color = random.choice(['Black', 'White'])
        question_text = f"How many '{stone_color}' stones are on the edge of the board?"  # noqa
        raw_answer = self._count_edge_stones(game_state, stone_color)
        return question_text, raw_answer, 'count'

    def _get_symbol_at_position(self, game_state, row, col):
        value = game_state[row][col]
        if value == 1:
            return 'Black'
        elif value == 2:
            return 'White'
        else:
            return 'empty'

    def _count_stones(self, game_state, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        return sum(row.count(stone_value) for row in game_state)

    def _count_stones_in_row(self, game_state, row, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        return game_state[row].count(stone_value)

    def _count_stones_in_column(self, game_state, col, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        return sum(1 for row in game_state if row[col] == stone_value)

    def _check_winning_condition(self, game_state):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(15):
            for col in range(15):
                if game_state[row][col] != 0:
                    stone_color = game_state[row][col]
                    for direction in directions:
                        count = 1
                        for step in range(1, 5):
                            x = row + step * direction[0]
                            y = col + step * direction[1]
                            if 0 <= x < 15 and 0 <= y < 15 and game_state[x][
                                    y] == stone_color:
                                count += 1
                            else:
                                break
                        if count >= 5:
                            return 'yes'
        return 'no'

    def _count_adjacent_stones(self, game_state, row, col):
        adjacent_positions = [(row - 1, col), (row + 1, col), (row, col - 1),
                              (row, col + 1), (row - 1, col - 1),
                              (row - 1, col + 1), (row + 1, col - 1),
                              (row + 1, col + 1)]
        count = 0
        for x, y in adjacent_positions:
            if 0 <= x < 15 and 0 <= y < 15 and game_state[x][y] != 0:
                count += 1
        return count

    def _count_empty_cells(self, game_state):
        return sum(row.count(0) for row in game_state)

    def _max_consecutive_in_row(self, game_state, row, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        max_consecutive = 0
        current_consecutive = 0
        for col in range(15):
            if game_state[row][col] == stone_value:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return max_consecutive

    def _max_consecutive_in_column(self, game_state, col, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        max_consecutive = 0
        current_consecutive = 0
        for row in range(15):
            if game_state[row][col] == stone_value:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return max_consecutive

    def _max_consecutive_on_diagonal(self, game_state, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        max_consecutive = 0
        for row in range(15):
            for col in range(15):
                for direction in [(1, 1), (1, -1)]:
                    current_consecutive = 0
                    for step in range(5):
                        x = row + step * direction[0]
                        y = col + step * direction[1]
                        if 0 <= x < 15 and 0 <= y < 15 and game_state[x][
                                y] == stone_value:
                            current_consecutive += 1
                            max_consecutive = max(max_consecutive,
                                                  current_consecutive)
                        else:
                            break
        return max_consecutive

    def _count_edge_stones(self, game_state, stone_color):
        stone_value = 1 if stone_color == 'Black' else 2
        count = 0
        count += sum(1 for i in range(1, 14)
                     if game_state[0][i] == stone_value)
        count += sum(1 for i in range(1, 14)
                     if game_state[14][i] == stone_value)
        count += sum(1 for i in range(1, 14)
                     if game_state[i][0] == stone_value)
        count += sum(1 for i in range(1, 14)
                     if game_state[i][14] == stone_value)
        corners = [
            game_state[0][0], game_state[0][14], game_state[14][0],
            game_state[14][14]
        ]
        count += sum(1 for corner in corners if corner == stone_value)
        return count


if __name__ == '__main__':
    gomoku_game_state = [[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    qa_system = GomokuQuestionAnswering(
        'Here is a screenshot of a Gomoku game.')
    for _ in range(5):
        question, answer = qa_system.get_qa_pair(gomoku_game_state)
        print(f'Q: {question}\nA: {answer}\n')
