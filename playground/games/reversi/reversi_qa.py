import random
import re

from playground.evaluator.base_qa import BaseQuestionAnswering


class ReversiQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_symbol_at_position_question,
            self._generate_count_symbol_question,
            self._generate_empty_cells_question,
            self._generate_row_column_count_question,
            self._generate_row_with_most_pieces_question,
            self._generate_compare_black_white_count_question,
            self._generate_row_column_sum_question,
            self._generate_total_count_question
        ]
        self._last_correct_answer = None
        self._last_options = None

    def _generate_mc_options(self, correct_answer: str, question_type: str):
        possible_options = []

        if question_type == 'symbol':
            base_pool = ['Black', 'White', 'empty']
            possible_options = list(set(base_pool + [correct_answer]))

        elif question_type == 'count':
            correct_num = int(correct_answer)
            nearby_nums = list(range(max(0, correct_num - 3), correct_num + 4))
            nearby_nums = [n for n in nearby_nums if n != correct_num]
            random.shuffle(nearby_nums)
            possible_options = [str(n) for n in nearby_nums[:3]]
            possible_options.append(str(correct_num))

        elif question_type == 'row_letter':
            all_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            if correct_answer in all_rows:
                all_rows.remove(correct_answer)
            random.shuffle(all_rows)
            possible_options = all_rows[:3] + [correct_answer]

        elif question_type == 'compare':
            base_pool = ['Black', 'White', 'equal']
            base_pool.append('tie')
            base_pool = list(set(base_pool))
            if correct_answer not in base_pool:
                base_pool.append(correct_answer)
            possible_options = base_pool

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

    def _format_mc_question(self, question_text, options):
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

    def _generate_symbol_at_position_question(self, game_state):
        row = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
        col = random.randint(1, 8)
        question_text = f'What is the symbol in row {row}, column {col}?'
        row_idx, col_idx = self._parse_position(row, col)
        raw_answer = self._get_symbol_at_position(game_state, row_idx, col_idx)
        return question_text, raw_answer, 'symbol'

    def _generate_count_symbol_question(self, game_state):
        symbol = random.choice(['Black', 'White'])
        question_text = f"How many '{symbol}' pieces are on the board?"
        raw_answer = self._count_symbol(game_state, symbol)
        return question_text, raw_answer, 'count'

    def _generate_empty_cells_question(self, game_state):
        question_text = 'How many empty cells are on the board?'
        raw_answer = self._count_empty_cells(game_state)
        return question_text, raw_answer, 'count'

    def _generate_row_column_count_question(self, game_state):
        axis = random.choice(['row', 'column'])
        symbol = random.choice(['Black', 'White'])
        if axis == 'row':
            row = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
            question_text = f"How many '{symbol}' pieces are in row {row}?"
            row_idx = self._row_to_index(row)
            raw_answer = self._count_symbol_in_row_column(
                game_state, 'row', row_idx, symbol)
        else:
            col = random.randint(1, 8)
            question_text = f"How many '{symbol}' pieces are in column {col}?"
            col_idx = col - 1
            raw_answer = self._count_symbol_in_row_column(
                game_state, 'column', col_idx, symbol)
        return question_text, raw_answer, 'count'

    def _generate_row_with_most_pieces_question(self, game_state):
        symbol = random.choice(['Black', 'White'])
        question_text = f"Which row has the most '{symbol}' pieces?"
        raw_answer = self._get_row_with_most_pieces(game_state, symbol)
        return question_text, raw_answer, 'row_letter'

    def _generate_compare_black_white_count_question(self, game_state):
        question_text = 'Which player has more pieces on the board?'
        raw_answer = self._compare_black_white_count(game_state)
        return question_text, raw_answer, 'compare'

    def _generate_row_column_sum_question(self, game_state):
        axis = random.choice(['row', 'column'])
        if axis == 'row':
            row = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
            question_text = f'How many pieces are in total in row {row}?'
            row_idx = self._row_to_index(row)
            raw_answer = self._sum_row_column(game_state, 'row', row_idx)
        else:
            col = random.randint(1, 8)
            question_text = f'How many pieces are in total in column {col}?'
            col_idx = col - 1
            raw_answer = self._sum_row_column(game_state, 'column', col_idx)
        return question_text, raw_answer, 'count'

    def _generate_total_count_question(self, game_state):
        symbol = random.choice(['Black', 'White'])
        question_text = f"How many '{symbol}' pieces are there in total on the board?"  # noqa
        raw_answer = self._count_symbol(game_state, symbol)
        return question_text, raw_answer, 'count'

    def _parse_position(self, row_letter, col_number):
        """Convert row letter, col number -> indices"""
        row_mapping = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            'F': 5,
            'G': 6,
            'H': 7
        }
        return row_mapping[row_letter], col_number - 1

    def _row_to_index(self, row_letter):
        row_mapping = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            'F': 5,
            'G': 6,
            'H': 7
        }
        return row_mapping[row_letter]

    def _get_symbol_at_position(self, game_state, row, col):
        try:
            value = game_state[row][col]
            if value == 1:
                return 'Black'
            elif value == 2:
                return 'White'
            else:
                return 'empty'
        except IndexError:
            return 'empty'

    def _count_symbol(self, game_state, symbol):
        symbol_value = 1 if symbol == 'Black' else 2
        return sum(row.count(symbol_value) for row in game_state)

    def _count_empty_cells(self, game_state):
        return sum(row.count(0) for row in game_state)

    def _count_symbol_in_row_column(self, game_state, axis, index, symbol):
        symbol_value = 1 if symbol == 'Black' else 2
        if axis == 'row':
            return game_state[index].count(symbol_value)
        else:
            return sum(1 for row in game_state if row[index] == symbol_value)

    def _sum_row_column(self, game_state, axis, index):
        if axis == 'row':
            return sum(1 for cell in game_state[index] if cell != 0)
        else:
            return sum(1 for row in game_state if row[index] != 0)

    def _get_row_with_most_pieces(self, game_state, symbol):
        symbol_value = 1 if symbol == 'Black' else 2
        row_counts = [row.count(symbol_value) for row in game_state]
        max_count = max(row_counts)
        row_index = row_counts.index(max_count)
        row_mapping = {
            0: 'A',
            1: 'B',
            2: 'C',
            3: 'D',
            4: 'E',
            5: 'F',
            6: 'G',
            7: 'H'
        }
        return row_mapping[row_index]

    def _compare_black_white_count(self, game_state):
        black_count = self._count_symbol(game_state, 'Black')
        white_count = self._count_symbol(game_state, 'White')
        if black_count > white_count:
            return 'Black'
        elif white_count > black_count:
            return 'White'
        else:
            return 'equal'


if __name__ == '__main__':
    reversi_game_state = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0],
        [0, 0, 1, 1, 2, 0, 0, 0],
        [0, 1, 2, 1, 2, 0, 0, 0],
        [0, 2, 1, 2, 1, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    qa_system = ReversiQuestionAnswering(
        'Here is a screenshot of a Reversi game.')

    for _ in range(5):
        question, answer = qa_system.get_qa_pair(reversi_game_state)
        print(f'Q: {question}\nA: {answer}\n')
