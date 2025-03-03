import random
import re
import string
from typing import Dict, Optional, Tuple

from playground.evaluator.base_qa import BaseQuestionAnswering


class MinesweeperQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_symbol_at_position_question,
            self._generate_count_mines_question,
            self._generate_revealed_cells_question,
            self._generate_row_column_count_question,
            self._generate_adjacent_revealed_mines_question,
            self._generate_adjacent_total_mines_question,
            self._generate_is_mine_at_position_question,
        ]
        self._last_correct_answer = None
        self._last_options = None

        self.board_size = None
        self._solution_state = None

    def _set_solution_state(self, solution_state):
        self._solution_state = solution_state

    def _generate_mc_options(self, correct_answer: str,
                             question_type: str) -> Tuple[Dict[str, str], str]:
        possible_options = []

        possible_pool = ['mine'] + [str(i) for i in range(9)]
        possible_options = list(set(possible_pool))
        if correct_answer not in possible_options:
            possible_options.append(correct_answer)

        elif question_type == 'count':
            correct_num = int(correct_answer)
            nearby_range = list(range(max(0, correct_num - 3),
                                      correct_num + 4))
            possible_options = [
                str(n) for n in nearby_range if n != correct_num
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
        insert_pos = random.randint(0, len(unique_options))
        unique_options.insert(insert_pos, correct_answer)

        option_letters = ['A', 'B', 'C', 'D']
        options = {}
        for i, val in enumerate(unique_options):
            options[option_letters[i]] = val

        correct_letter = None
        for letter, val in options.items():
            if val == correct_answer:
                correct_letter = letter
                break

        return options, correct_letter

    def _format_mc_question(self, question_text: str,
                            options: Dict[str, str]) -> str:
        question_text = re.sub(r'Please respond with.*', '',
                               question_text).strip()
        formatted_question = f'{question_text}\n'
        for letter, val in options.items():
            formatted_question += f'{letter}. {val}\n'
        return formatted_question.strip()

    def get_qa_pair(self, game_state):
        if self.board_size is None:
            self.board_size = len(game_state)

        while True:
            question_func = random.choice(self.question_pool)
            result = question_func(game_state)
            if result is None:
                continue

            question_text, raw_answer, question_type = result
            options, correct_letter = self._generate_mc_options(
                str(raw_answer), question_type)
            self._last_correct_answer = correct_letter
            self._last_options = options

            formatted_question = self._format_mc_question(
                question_text, options)
            return formatted_question, correct_letter

    def get_answer(self, game_state, question):
        if self._last_correct_answer is not None and self._last_options is not None:  # noqa
            ans = self._last_correct_answer
            self._last_correct_answer = None
            self._last_options = None
            return ans
        return 'No stored multiple-choice answer.'

    def _generate_symbol_at_position_question(self, game_state):
        while True:
            row_label = random.choice(string.ascii_lowercase[:len(game_state)])
            col = random.randint(1, len(game_state))
            if game_state[ord(row_label) - ord('a')][col - 1] != -1:
                question_text = f'What is the revealed symbol in row {row_label}, column {col}?'  # noqa
                raw_answer = self._get_symbol_at_position(
                    game_state,
                    ord(row_label) - ord('a'), col - 1)
                return question_text, raw_answer, 'symbol'

    def _generate_count_mines_question(self, game_state):
        question_text = 'How many revealed mines are there on the board?'
        raw_answer = self._count_mines(game_state)
        return question_text, raw_answer, 'count'

    def _generate_revealed_cells_question(self, game_state):
        question_text = 'How many revealed cells are there on the board?'
        raw_answer = self._count_revealed_cells(game_state)
        return question_text, raw_answer, 'count'

    def _generate_row_column_count_question(self, game_state):
        axis = random.choice(['row', 'column'])
        size = len(game_state)
        if axis == 'row':
            row_label = random.choice(string.ascii_lowercase[:size])
            question_text = f'How many revealed cells are there in row {row_label}?'  # noqa
            idx = ord(row_label) - ord('a')
            raw_answer = self._count_revealed_in_row_column(
                game_state, 'row', idx)
        else:
            col = random.randint(1, size)
            question_text = f'How many revealed cells are there in column {col}?'  # noqa
            idx = col - 1
            raw_answer = self._count_revealed_in_row_column(
                game_state, 'column', idx)
        return question_text, raw_answer, 'count'

    def _generate_adjacent_revealed_mines_question(self, game_state):
        valid_cells = []
        for r in range(len(game_state)):
            for c in range(len(game_state)):
                val = game_state[r][c]
                if 0 <= val <= 8:
                    valid_cells.append((r, c))

        if not valid_cells:
            return None
        row, col = random.choice(valid_cells)
        row_label = chr(row + ord('a'))
        question_text = f'How many revealed mines are adjacent to row {row_label}, column {col+1}?'  # noqa

        revealed_mines = self._get_adjacent_revealed_mines(
            game_state, row, col)
        return question_text, revealed_mines, 'count'

    def _generate_adjacent_total_mines_question(
            self, game_state) -> Optional[Tuple[str, int, str]]:
        if self._solution_state is None:
            return None

        valid_cells = []
        for r in range(len(game_state)):
            for c in range(len(game_state)):
                val = game_state[r][c]
                if 0 <= val <= 8:
                    valid_cells.append((r, c))

        if not valid_cells:
            return None
        row, col = random.choice(valid_cells)
        row_label = chr(row + ord('a'))

        question_text = f'How many total mines (revealed or not) are adjacent to row {row_label}, column {col+1}?'  # noqa
        total_mines = self._get_adjacent_total_mines(row, col)
        return question_text, total_mines, 'count'

    def _generate_is_mine_at_position_question(self, game_state):
        while True:
            row_label = random.choice(string.ascii_lowercase[:len(game_state)])
            col = random.randint(1, len(game_state))
            if game_state[ord(row_label) - ord('a')][col - 1] != -1:
                question_text = f'Is there a revealed mine at row {row_label}, column {col}?'  # noqa
                raw_answer = self._is_mine_at_position(
                    game_state,
                    ord(row_label) - ord('a'), col - 1)
                return question_text, raw_answer, 'yes_no'

    def _get_symbol_at_position(self, game_state, row, col):
        value = game_state[row][col]
        return 'mine' if value == 9 else str(value)  # 0~8

    def _count_mines(self, game_state):
        return sum(row.count(9) for row in game_state)

    def _count_revealed_cells(self, game_state):
        return sum(cell != -1 for row in game_state for cell in row)

    def _count_revealed_in_row_column(self, game_state, axis, index):
        if axis == 'row':
            return sum(cell != -1 for cell in game_state[index])
        elif axis == 'column':
            return sum(row[index] != -1 for row in game_state)

    def _get_adjacent_revealed_mines(self, game_state, row, col) -> int:
        surrounding = [
            game_state[y][x]
            for x in range(max(0, col - 1), min(col + 2, len(game_state)))
            for y in range(max(0, row - 1), min(row + 2, len(game_state)))
            if not (x == col and y == row)
        ]
        return sum(1 for val in surrounding if val == 9)

    def _get_adjacent_total_mines(self, row, col) -> int:
        if self._solution_state is None:
            return 0

        surrounding = [
            self._solution_state[y][x]
            for x in range(max(0, col -
                               1), min(col + 2, len(self._solution_state)))
            for y in range(max(0, row -
                               1), min(row + 2, len(self._solution_state)))
            if not (x == col and y == row)
        ]
        return sum(1 for val in surrounding if val == 9)

    def _is_mine_at_position(self, game_state, row, col):
        return 'yes' if game_state[row][col] == 9 else 'no'


if __name__ == '__main__':
    minesweeper_game_state = [
        [-1, -1, 1, 9, 1, -1, -1, -1],
        [-1, -1, 1, 1, 2, 1, -1, -1],
        [-1, 1, 1, 0, 1, 9, 2, 1],
        [-1, 1, 9, 1, 1, 2, 9, 1],
        [1, 2, 2, 1, 0, 1, 1, 1],
        [9, 2, 9, 1, 0, 1, 1, 9],
        [1, 2, 3, 2, 1, 9, 3, 9],
        [0, 1, 9, 9, 2, 2, 2, 1],
    ]

    solution_state = [
        [0, 0, 0, 9, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 9, 0, 0],
        [0, 0, 9, 0, 0, 0, 9, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [9, 0, 9, 0, 0, 0, 0, 9],
        [0, 0, 0, 0, 0, 9, 0, 9],
        [0, 0, 9, 9, 0, 0, 0, 0],
    ]

    qa_system = MinesweeperQuestionAnswering(
        'Here is a screenshot of a Minesweeper game.')
    qa_system._set_solution_state(solution_state)

    for _ in range(5):
        question, answer = qa_system.get_qa_pair(minesweeper_game_state)
        print(f'Q: {question}\nA: {answer}\n')
