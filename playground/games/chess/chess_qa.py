import random

from playground.evaluator.base_qa import BaseQuestionAnswering


class ChessQuestionAnswering(BaseQuestionAnswering):

    def __init__(self, general_prompt):
        super().__init__(general_prompt)
        self.question_pool = [
            self._generate_piece_color_at_position_question,
            self._generate_piece_name_at_position_question,
            self._generate_count_pieces_question,
            self._generate_row_column_count_question,
            self._generate_more_white_or_black_question,
            self._generate_piece_comparison_question,
            self._generate_edge_pieces_count_question,
            self._generate_empty_half_board_question
        ]
        self.rows = '87654321'
        self.cols = 'abcdefgh'
        self._last_correct_answer = None
        self._last_options = None

    def _generate_mc_options(self, correct_answer: str, question_type: str):
        possible_options = []

        if question_type == 'color':
            base_pool = ['white', 'black', 'empty']
            if correct_answer not in base_pool:
                base_pool.append(correct_answer)
            possible_options = base_pool

        elif question_type == 'piece_name':
            base_pool = [
                'pawn', 'knight', 'bishop', 'rook', 'queen', 'king', 'empty'
            ]
            base_pool.append('unknown')
            base_pool = list(set(base_pool))
            if correct_answer not in base_pool:
                base_pool.append(correct_answer)
            possible_options = base_pool

        elif question_type == 'count':
            correct_num = int(correct_answer)
            nearby = list(range(max(0, correct_num - 3), correct_num + 4))
            nearby = [n for n in nearby if n != correct_num]
            random.shuffle(nearby)
            possible_options = [str(n) for n in nearby[:3]]
            possible_options.append(str(correct_num))

        elif question_type == 'compare_color':
            base_pool = ['white', 'black', 'equal']
            if correct_answer not in base_pool:
                base_pool.append(correct_answer)
            possible_options = base_pool

        elif question_type == 'compare_pieces':
            base_pool = [
                'pawn', 'knight', 'bishop', 'rook', 'queen', 'king', 'equal'
            ]
            if correct_answer not in base_pool:
                base_pool.append(correct_answer)
            possible_options = base_pool

        elif question_type == 'compare_halves':
            base_pool = ['top', 'bottom', 'equal']
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

    def _format_mc_question(self, question_text: str, options: dict):
        for phrase in ['Please respond with', 'Please answer with']:
            if phrase in question_text:
                question_text = question_text.split(phrase)[0].strip()

        formatted = question_text.strip() + '\n'
        for letter, val in options.items():
            formatted += f'{letter}. {val}\n'
        return formatted.strip()

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

    def _generate_piece_color_at_position_question(self, game_state):
        row_idx = random.randint(0, 7)
        col_idx = random.randint(0, 7)
        row_label = self.rows[row_idx]  # '87654321'
        col_label = self.cols[col_idx]  # 'abcdefgh'
        question_text = f'What is the color of the piece at column {col_label}, row {row_label}?'  # noqa
        raw_answer = self._get_piece_color_at_position(game_state, row_idx,
                                                       col_idx)
        return question_text, raw_answer, 'color'

    def _generate_piece_name_at_position_question(self, game_state):
        row_idx = random.randint(0, 7)
        col_idx = random.randint(0, 7)
        row_label = self.rows[row_idx]
        col_label = self.cols[col_idx]
        question_text = f'What is the piece at column {col_label}, row {row_label}?'  # noqa
        raw_answer = self._get_piece_name_at_position(game_state, row_idx,
                                                      col_idx)
        return question_text, raw_answer, 'piece_name'

    def _generate_count_pieces_question(self, game_state):
        piece_type = random.choice(
            ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k'])
        piece_color = 'white' if piece_type.isupper() else 'black'
        piece_name = self._piece_name(piece_type)
        question_text = f'How many {piece_color} {piece_name}s are on the board?'  # noqa
        raw_answer = self._count_pieces(game_state, piece_type)
        return question_text, raw_answer, 'count'

    def _generate_row_column_count_question(self, game_state):
        axis = random.choice(['row', 'column'])
        if axis == 'row':
            row_idx = random.randint(0, 7)
            row_label = self.rows[row_idx]
            question_text = f'How many pieces are in row {row_label}?'
            raw_answer = self._count_pieces_in_row(game_state, row_idx)
        else:
            col_idx = random.randint(0, 7)
            col_label = self.cols[col_idx]
            question_text = f'How many pieces are in column {col_label}?'
            raw_answer = self._count_pieces_in_column(game_state, col_idx)
        return question_text, raw_answer, 'count'

    def _generate_more_white_or_black_question(self, game_state):
        """Which color has more pieces? -> 'white', 'black', or 'equal'."""
        white_count = self._count_pieces_by_color(game_state, 'white')
        black_count = self._count_pieces_by_color(game_state, 'black')
        if white_count > black_count:
            raw_answer = 'white'
        elif black_count > white_count:
            raw_answer = 'black'
        else:
            raw_answer = 'equal'
        question_text = 'Which color has more pieces on the board?'
        return question_text, raw_answer, 'compare_color'

    def _generate_piece_comparison_question(self, game_state):
        piece_list = [
            'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k'
        ]
        piece1, piece2 = random.sample(piece_list, 2)
        piece1_name = self._piece_name(piece1)
        piece2_name = self._piece_name(piece2)
        p1_count = self._count_pieces(game_state, piece1)
        p2_count = self._count_pieces(game_state, piece2)
        if p1_count > p2_count:
            raw_answer = piece1_name
        elif p2_count > p1_count:
            raw_answer = piece2_name
        else:
            raw_answer = 'equal'
        question_text = f'Which has more, {piece1_name}s or {piece2_name}s?'
        return question_text, raw_answer, 'compare_pieces'

    def _generate_edge_pieces_count_question(self, game_state):
        question_text = 'How many pieces are on the edge of the board?'
        raw_answer = self._count_edge_pieces(game_state)
        return question_text, raw_answer, 'count'

    def _generate_empty_half_board_question(self, game_state):
        top_empty = self._count_empty_cells_in_half(game_state, 'top')
        bottom_empty = self._count_empty_cells_in_half(game_state, 'bottom')
        if top_empty > bottom_empty:
            raw_answer = 'top'
        elif bottom_empty > top_empty:
            raw_answer = 'bottom'
        else:
            raw_answer = 'equal'
        question_text = 'Which half of the board has more empty cells?'
        return question_text, raw_answer, 'compare_halves'

    def _get_piece_color_at_position(self, game_state, row, col):
        piece_value = game_state[row][col]
        if piece_value == 0:
            return 'empty'
        elif piece_value > 0:
            return 'white'
        else:
            return 'black'

    def _get_piece_name_at_position(self, game_state, row, col):
        piece_value = game_state[row][col]
        if piece_value == 0:
            return 'empty'
        piece_names = {
            1: 'pawn',
            2: 'knight',
            3: 'bishop',
            4: 'rook',
            5: 'queen',
            6: 'king',
            -1: 'pawn',
            -2: 'knight',
            -3: 'bishop',
            -4: 'rook',
            -5: 'queen',
            -6: 'king'
        }
        return piece_names.get(piece_value, 'unknown')

    def _count_pieces(self, game_state, piece_type):
        piece_mapping = {
            'P': 1,
            'N': 2,
            'B': 3,
            'R': 4,
            'Q': 5,
            'K': 6,
            'p': -1,
            'n': -2,
            'b': -3,
            'r': -4,
            'q': -5,
            'k': -6
        }
        target_value = piece_mapping[piece_type]
        return sum(row.count(target_value) for row in game_state)

    def _piece_name(self, piece_type):
        piece_names = {
            'P': 'pawn',
            'N': 'knight',
            'B': 'bishop',
            'R': 'rook',
            'Q': 'queen',
            'K': 'king',
            'p': 'pawn',
            'n': 'knight',
            'b': 'bishop',
            'r': 'rook',
            'q': 'queen',
            'k': 'king'
        }
        return piece_names[piece_type]

    def _count_pieces_in_row(self, game_state, row):
        return sum(1 for piece in game_state[row] if piece != 0)

    def _count_pieces_in_column(self, game_state, col):
        return sum(1 for row in game_state if row[col] != 0)

    def _count_pieces_by_color(self, game_state, color):
        return sum(1 for row in game_state for piece in row
                   if (color == 'white' and piece > 0) or (
                       color == 'black' and piece < 0))

    def _count_edge_pieces(self, game_state):
        count = sum(1 for piece in game_state[0][1:7] if piece != 0)
        count += sum(1 for piece in game_state[7][1:7] if piece != 0)
        count += sum(1 for row in game_state[1:7] if row[0] != 0)
        count += sum(1 for row in game_state[1:7] if row[7] != 0)

        corners = [
            game_state[0][0], game_state[0][7], game_state[7][0],
            game_state[7][7]
        ]
        count += sum(1 for corner in corners if corner != 0)

        return count

    def _count_empty_cells_in_half(self, game_state, half):
        if half == 'top':
            return sum(row.count(0) for row in game_state[:4])
        else:
            return sum(row.count(0) for row in game_state[4:])


if __name__ == '__main__':
    chess_game_state = [
        [4, 2, 3, 5, 6, 3, 2, 4],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [-4, -2, -3, -5, -6, -3, -2, -4],
    ]

    qa_system = ChessQuestionAnswering('Here is a screenshot of a Chess game.')
    for _ in range(5):
        question, answer = qa_system.get_qa_pair(chess_game_state)
        print(f'Q: {question}\nA: {answer}\n')
