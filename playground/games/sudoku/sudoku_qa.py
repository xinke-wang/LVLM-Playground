import random
import re

from playground.evaluator.base_qa import BaseQuestionAnswering


class SudokuQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_symbol_at_position_question,
            self._generate_count_symbol_question,
            self._generate_empty_cells_question,
            self._generate_row_column_count_question,
            self._generate_subgrid_count_question,
            self._generate_row_column_sum_question,
            self._generate_subgrid_sum_question,
            self._generate_row_column_contains_question,
            self._generate_subgrid_empty_count_question
        ]
        self._last_correct_answer = None
        self._last_options = None

    def _generate_mc_options(self, correct_answer: str, question_type: str):
        possible_options = []

        if question_type == 'symbol':
            base_pool = [str(n) for n in range(1, 10)] + ['empty']
            possible_options = list(set(base_pool + [correct_answer]))
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

        elif question_type == 'sum':
            correct_sum = int(correct_answer)
            nearby_range = list(range(max(0, correct_sum - 5),
                                      correct_sum + 6))
            possible_options = [
                str(n) for n in nearby_range if n != correct_sum
            ]
            random.shuffle(possible_options)
            possible_options = possible_options[:3]
            possible_options.append(str(correct_sum))

        elif question_type == 'yes_no':
            possible_options = ['yes', 'no']
            possible_options += ['maybe', 'unknown']
            possible_options = list(set(possible_options))
            if correct_answer not in possible_options:
                possible_options.append(correct_answer)
        else:
            possible_options = [correct_answer, '???', '???2', '???3']

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

    def _format_mc_question(self, question_text: str, options: dict):
        question_text = re.sub(r'Please respond with.*', '',
                               question_text).strip()
        formatted_question = f'{question_text}\n'
        for letter, val in options.items():
            formatted_question += f'{letter}. {val}\n'
        return formatted_question.strip()

    def get_qa_pair(self, game_state):
        while True:
            question_func = random.choice(self.question_pool)
            result = question_func(game_state)
            if not result:
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

    def _generate_symbol_at_position_question(self, _game_state):
        row = random.randint(1, 9)
        col = random.randint(1, 9)
        question_text = f'What is the number in row {row}, column {col}?'
        row_idx, col_idx = row - 1, col - 1
        raw_answer = self._get_symbol_at_position(_game_state, row_idx,
                                                  col_idx)
        return question_text, raw_answer, 'symbol'

    def _generate_count_symbol_question(self, _game_state):
        number = random.randint(1, 9)
        question_text = f"How many '{number}'s are present on the board?"
        raw_answer = self._count_symbol(_game_state, number)
        return question_text, raw_answer, 'count'

    def _generate_empty_cells_question(self, _game_state):
        question_text = 'How many empty cells are on the board?'
        raw_answer = self._count_empty_cells(_game_state)
        return question_text, raw_answer, 'count'

    def _generate_row_column_count_question(self, _game_state):
        axis = random.choice(['row', 'column'])
        number = random.randint(1, 9)
        if axis == 'row':
            row = random.randint(1, 9)
            question_text = f"How many '{number}'s are in row {row}?"
            index = row - 1
            raw_answer = self._count_symbol_in_row_column(
                _game_state, axis, index, number)
        else:
            col = random.randint(1, 9)
            question_text = f"How many '{number}'s are in column {col}?"
            index = col - 1
            raw_answer = self._count_symbol_in_row_column(
                _game_state, axis, index, number)
        return question_text, raw_answer, 'count'

    def _generate_subgrid_count_question(self, _game_state):
        number = random.randint(1, 9)
        subgrid_row = random.randint(1, 3)
        subgrid_col = random.randint(1, 3)
        start_r = (subgrid_row - 1) * 3 + 1
        start_c = (subgrid_col - 1) * 3 + 1
        question_text = f"How many '{number}'s are in the subgrid starting at row {start_r}, column {start_c}?"  # noqa
        raw_answer = self._count_symbol_in_subgrid(_game_state, number,
                                                   start_r, start_c)
        return question_text, raw_answer, 'count'

    def _generate_row_column_sum_question(self, _game_state):
        axis = random.choice(['row', 'column'])
        if axis == 'row':
            row = random.randint(1, 9)
            question_text = f'What is the sum of numbers in row {row}?'
            index = row - 1
            raw_answer = self._sum_row_column(_game_state, axis, index)
        else:
            col = random.randint(1, 9)
            question_text = f'What is the sum of numbers in column {col}?'
            index = col - 1
            raw_answer = self._sum_row_column(_game_state, axis, index)
        return question_text, raw_answer, 'sum'

    def _generate_subgrid_sum_question(self, _game_state):
        subgrid_row = random.randint(1, 3)
        subgrid_col = random.randint(1, 3)
        start_r = (subgrid_row - 1) * 3 + 1
        start_c = (subgrid_col - 1) * 3 + 1
        question_text = (
            f'What is the sum of numbers in the subgrid starting at row {start_r}, column {start_c}?'  # noqa
        )
        raw_answer = self._sum_subgrid(_game_state, start_r, start_c)
        return question_text, raw_answer, 'sum'

    def _generate_row_column_contains_question(self, _game_state):
        axis = random.choice(['row', 'column'])
        number = random.randint(1, 9)
        if axis == 'row':
            row = random.randint(1, 9)
            question_text = f"Does row {row} contain the number '{number}'?"
            index = row - 1
        else:
            col = random.randint(1, 9)
            question_text = f"Does column {col} contain the number '{number}'?"
            index = col - 1

        raw_answer = self._contains_number(_game_state, axis, index, number)
        return question_text, raw_answer, 'yes_no'

    def _generate_subgrid_empty_count_question(self, _game_state):
        subgrid_row = random.randint(1, 3)
        subgrid_col = random.randint(1, 3)
        start_r = (subgrid_row - 1) * 3 + 1
        start_c = (subgrid_col - 1) * 3 + 1
        question_text = (
            f'How many empty cells are in the subgrid starting at row {start_r}, column {start_c}?'  # noqa
        )
        raw_answer = self._count_empty_in_subgrid(_game_state, start_r,
                                                  start_c)
        return question_text, raw_answer, 'count'

    def _get_symbol_at_position(self, game_state, row, col):
        try:
            value = game_state[row][col]
            return str(value) if value != 0 else 'empty'
        except IndexError:
            return 'empty'

    def _count_symbol(self, game_state, symbol):
        return sum(row.count(symbol) for row in game_state)

    def _count_empty_cells(self, game_state):
        return sum(row.count(0) for row in game_state)

    def _count_symbol_in_row_column(self, game_state, axis, index, symbol):
        if axis == 'row':
            return game_state[index].count(symbol)
        elif axis == 'column':
            return sum(1 for row in game_state if row[index] == symbol)

    def _sum_row_column(self, game_state, axis, index):
        if axis == 'row':
            return sum(game_state[index])
        else:  # 'column'
            return sum(row[index] for row in game_state)

    def _count_symbol_in_subgrid(self, game_state, symbol, start_r, start_c):
        sr = start_r - 1
        sc = start_c - 1
        cnt = 0
        for i in range(3):
            for j in range(3):
                if game_state[sr + i][sc + j] == symbol:
                    cnt += 1
        return cnt

    def _count_empty_in_subgrid(self, game_state, start_r, start_c):
        sr = start_r - 1
        sc = start_c - 1
        cnt = 0
        for i in range(3):
            for j in range(3):
                if game_state[sr + i][sc + j] == 0:
                    cnt += 1
        return cnt

    def _sum_subgrid(self, game_state, start_r, start_c):
        sr = start_r - 1
        sc = start_c - 1
        total = 0
        for i in range(3):
            for j in range(3):
                total += game_state[sr + i][sc + j]
        return total

    def _contains_number(self, game_state, axis, index, number):
        if axis == 'row':
            return 'yes' if number in game_state[index] else 'no'
        else:
            return 'yes' if any(row[index] == number
                                for row in game_state) else 'no'


if __name__ == '__main__':
    sudoku_game_state = [
        [0, 1, 5, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 4, 1, 0, 0, 0, 5],
        [0, 4, 0, 0, 0, 0, 0, 7, 1],
        [1, 0, 2, 5, 0, 0, 6, 4, 0],
        [0, 7, 0, 0, 6, 4, 0, 5, 0],
        [0, 0, 4, 0, 0, 0, 1, 0, 0],
        [0, 0, 9, 0, 5, 1, 0, 3, 0],
        [8, 0, 1, 3, 0, 0, 0, 2, 4],
        [0, 0, 6, 2, 0, 0, 5, 0, 0],
    ]

    qa_system = SudokuQuestionAnswering(
        'Here is a screenshot of a Sudoku game.')

    for _ in range(5):
        question, answer = qa_system.get_qa_pair(sudoku_game_state)
        print(f'Q: {question}\nA: {answer}\n')
