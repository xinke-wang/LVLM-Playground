import random
import re
from typing import Dict, Optional, Tuple

from playground.evaluator.base_qa import BaseQuestionAnswering


class TicTacToeQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_symbol_at_position_question,
            self._generate_count_symbol_question,
            self._generate_empty_cells_question,
            self._generate_row_column_count_question,
            self._generate_red_blue_count_question
        ]
        self._last_correct_answer = None
        self._last_options = None

    def _generate_mc_options(self, correct_answer: str,
                             question_type: str) -> Tuple[Dict[str, str], str]:
        possible_options = []
        if question_type == 'symbol':
            possible_options = ['X', 'O', 'empty']
            if str(correct_answer) not in possible_options:
                possible_options.append(str(correct_answer))
        elif question_type == 'count':
            correct_num = int(correct_answer)
            possible_range = list(
                range(max(0, correct_num - 3), correct_num + 4))
            possible_options = [
                str(num) for num in possible_range
                if str(num) != str(correct_answer)
            ]
            random.shuffle(possible_options)
            possible_options = possible_options[:3]
            possible_options.append(str(correct_answer))
        elif question_type == 'winner':
            possible_options = ['X', 'O', 'No winner yet.']
            if str(correct_answer) not in possible_options:
                possible_options.append(str(correct_answer))
        if str(correct_answer) in possible_options:
            possible_options.remove(str(correct_answer))

        random.shuffle(possible_options)

        unique_options = []
        seen = set()
        for opt in possible_options:
            if opt not in seen and len(unique_options) < 3:
                unique_options.append(opt)
                seen.add(opt)
        insert_position = random.randint(0, len(unique_options))
        unique_options.insert(insert_position, str(correct_answer))
        options = {}
        option_letters = ['A', 'B', 'C', 'D']
        for i, option in enumerate(unique_options):
            options[option_letters[i]] = option

        for letter, value in options.items():
            if value == str(correct_answer):
                correct_position = letter
                break

        return options, correct_position

    def _format_mc_question(self, question: str, options: Dict[str,
                                                               str]) -> str:
        question = re.sub(r'Please respond with.*\.', '', question).strip()
        formatted_question = f'{question}\n'
        for option, value in options.items():
            formatted_question += f'{option}. {value}\n'
        return formatted_question.strip()

    def _generate_symbol_at_position_question(self) -> Tuple[str, str]:
        row = random.choice(['A', 'B', 'C'])
        col = random.randint(1, 3)
        return f'What is the symbol in row {row}, column {col}?', 'symbol'

    def _generate_count_symbol_question(self) -> Tuple[str, str]:
        symbol = random.choice(['X', 'O'])
        return f"How many '{symbol}'s are present on the board?", 'count'

    def _generate_winner_question(self,
                                  game_state) -> Optional[Tuple[str, str]]:
        winner = self._check_winner(game_state)
        if winner in ['X', 'O']:
            return 'Did X or O win the game?', 'winner'
        return None

    def _generate_empty_cells_question(self) -> Tuple[str, str]:
        return 'How many empty cells are there?', 'count'

    def _generate_row_column_count_question(self) -> Tuple[str, str]:
        axis = random.choice(['row', 'column'])
        element = random.choice(['X', 'O', 'empty'])
        if axis == 'row':
            row = random.choice(['A', 'B', 'C'])
            return f"How many '{element}'s are there in row {row}?", 'count'
        else:
            col = random.randint(1, 3)
            return f"How many '{element}'s are there in column {col}?", 'count'

    def _generate_red_blue_count_question(self) -> Tuple[str, str]:
        color = random.choice(['red', 'blue'])
        context = random.choice(['board', 'row', 'column'])

        if context == 'board':
            return f'How many {color} marks are present on the board?', 'count'
        elif context == 'row':
            row = random.choice(['A', 'B', 'C'])
            return f'How many {color} marks are there in row {row}?', 'count'
        else:
            col = random.randint(1, 3)
            return f'How many {color} marks are there in column {col}?', 'count'  # noqa

    def get_qa_pair(self, game_state):
        while True:
            question_func = random.choice(self.question_pool)
            base_question, question_type = question_func()
            if random.random() < 0.2:
                winner_question = self._generate_winner_question(game_state)
                if winner_question:
                    base_question, question_type = winner_question
            raw_answer = self._get_raw_answer(game_state, base_question)
            if 'win the game' in base_question and raw_answer in [
                    'Both players won', 'No winner yet.'
            ]:
                continue
            options, correct_letter = self._generate_mc_options(
                raw_answer, question_type)
            self._last_correct_answer = correct_letter
            self._last_options = options
            formatted_question = self._format_mc_question(
                base_question, options)
            return formatted_question, correct_letter

    def get_answer(self, game_state, question):
        if self._last_correct_answer is not None and self._last_options is not None:  # noqa
            tmp_answer = self._last_correct_answer
            self._last_correct_answer = None
            self._last_options = None
            return tmp_answer
        return self._get_raw_answer(game_state, question)

    def _get_raw_answer(self, game_state, question):
        if question.startswith('What is the symbol in row'):
            row, col = self._parse_position_question(question)
            return self._get_symbol_at_position(game_state, row, col)
        elif question.startswith("How many '") or 'marks' in question:
            symbol = question.split(
                "'"
            )[1] if 'marks' not in question else self._get_symbol_from_color(
                question)
            if 'row' in question or 'column' in question:
                axis, index = self._parse_row_column_question(question)
                return str(
                    self._count_symbol_in_row_column(game_state, axis, index,
                                                     symbol))
            else:
                return str(self._count_symbol(game_state, symbol))
        elif 'empty cells' in question:
            return str(self._count_empty_cells(game_state))
        elif 'win the game' in question:
            return self._check_winner(game_state)
        else:
            return 'Unknown question'

    def _parse_position_question(self, question):
        row_mapping = {'A': 0, 'B': 1, 'C': 2}
        match = re.search(r'row\s+([ABC]),\s*column\s+(\d)', question)
        if match:
            row_letter = match.group(1)
            col = int(match.group(2)) - 1
            row = row_mapping[row_letter]
            return row, col
        else:
            raise ValueError('Could not parse position from question')

    def _get_symbol_at_position(self, game_state, row, col):
        try:
            value = game_state[row][col]
            if value == 1:
                return 'X'
            elif value == 0:
                return 'O'
            else:
                return 'empty'
        except IndexError:
            return 'Invalid position'

    def _count_symbol(self, game_state, symbol):
        symbol_value = 1 if symbol == 'X' else 0
        return sum(row.count(symbol_value) for row in game_state)

    def _count_empty_cells(self, game_state):
        return sum(row.count(-1) for row in game_state)

    def _parse_row_column_question(self, question):
        row_mapping = {'A': 0, 'B': 1, 'C': 2}
        if 'row' in question:
            match = re.search(r'row\s+([ABC])', question)
            if match:
                row_letter = match.group(1)
                return 'row', row_mapping[row_letter]
            else:
                raise ValueError('Could not parse row from question')
        elif 'column' in question:
            match = re.search(r'column\s+(\d)', question)
            if match:
                col_num = int(match.group(1)) - 1
                return 'column', col_num
            else:
                raise ValueError('Could not parse column from question')
        else:
            raise ValueError(
                'Question does not contain row or column information')

    def _count_symbol_in_row_column(self, game_state, axis, index, symbol):
        symbol_value = 1 if symbol == 'X' else 0 if symbol == 'O' else -1
        if axis == 'row':
            return game_state[index].count(symbol_value)
        elif axis == 'column':
            return sum(1 for row in game_state if row[index] == symbol_value)

    def _check_winner(self, game_state):
        x_wins = o_wins = False

        # Check rows
        for row in game_state:
            if row[0] == row[1] == row[2] and row[0] != -1:
                if row[0] == 1:
                    x_wins = True
                elif row[0] == 0:
                    o_wins = True
        for col in range(3):
            if game_state[0][col] == game_state[1][col] == game_state[2][
                    col] and game_state[0][col] != -1:
                if game_state[0][col] == 1:
                    x_wins = True
                elif game_state[0][col] == 0:
                    o_wins = True
        if game_state[0][0] == game_state[1][1] == game_state[2][
                2] and game_state[0][0] != -1:
            if game_state[0][0] == 1:
                x_wins = True
            elif game_state[0][0] == 0:
                o_wins = True
        if game_state[0][2] == game_state[1][1] == game_state[2][
                0] and game_state[0][2] != -1:
            if game_state[0][2] == 1:
                x_wins = True
            elif game_state[0][2] == 0:
                o_wins = True

        if x_wins and o_wins:
            return 'Both players won'
        elif x_wins:
            return 'X'
        elif o_wins:
            return 'O'
        else:
            return 'No winner yet.'

    def _get_symbol_from_color(self, question):
        if 'red' in question:
            return 'X'
        else:
            return 'O'


if __name__ == '__main__':
    tic_tac_toe_game_state = [[1, 0, -1], [0, 1, 0], [1, -1, 1]]

    qa_system = TicTacToeQuestionAnswering(
        'Here is a screenshot of a Tic Tac Toe game.')
    for _ in range(5):
        question, answer = qa_system.get_qa_pair(tic_tac_toe_game_state)
        print(f'Q: {question}\nA: {answer}\n')
