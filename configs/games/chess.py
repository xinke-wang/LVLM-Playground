from playground.games import ChessQuestionAnswering

_base_ = ['configs/base.py']

game_name = 'chess'
game_description = dict(
    e2e=(
        'Chess is a strategy game played on an 8x8 board with 64 squares, '
        'using six types of pieces: pawns, knights, bishops, rooks, queens, '
        'and kings, for both white and black players. The game starts with a '
        'standard initial position: white pieces on ranks 1 and 2, black '
        'pieces on ranks 7 and 8. The board uses algebraic coordinates with '
        'files labeled "a" through "h" from left to right and ranks labeled '
        '"1" through "8" from bottom to top (a1 at bottom-left, h8 at '
        'top-right). White moves first, followed by Black. You are playing as '
        'White, aiming to checkmate the Black king or achieve a favorable '
        'position. Each move must follow standard chess rules and be '
        'expressed in Standard Algebraic Notation (SAN), such as "e4" (pawn '
        'to e4), "Nf3" (knight to f3), or "O-O" (kingside castling). Based on '
        'the board state screenshots, please first observe the current '
        'situation, then carefully think and explain your strategy briefly, '
        'and finally output your movement for this status. Please strictly '
        'follow the following format:\n'
        'Observation: <observation>\n'
        'Strategy: <strategy>\n'
        'Movement: <position>\n'
        'where the observation should briefly summarize the current '
        'situation, the strategy is a brief explanation of how you plan to '
        'win or improve your position, and the position is a legal move in '
        'SAN, for example, "e4", "Nf3", or "O-O".'
    ),
    perceive=(
        'Chess is a strategy game played on an 8x8 board with 64 squares, '
        'using six types of pieces: pawns, knights, bishops, rooks, queens, '
        'and kings, for both white and black players. You are provided with '
        'an image of a chessboard, and your task is to represent the current '
        'state of the game as an 8x8 matrix using the specified numerical '
        'format. Each type of chess piece, both black and white, is '
        'represented by a unique number:\n- Empty squares: 0\n'
        '- White pieces: Pawn=1, Knight=2, Bishop=3, Rook=4, Queen=5, King=6\n'
        '- Black pieces: Pawn=-1, Knight=-2, Bishop=-3, Rook=-4, Queen=-5, '
        'King=-6\n\nFrom the provided chessboard image, convert the visible '
        'board into this 8x8 matrix format. For example, the initial chess '
        'position would be represented as:\n'
        'Game State: [[-4, -2, -3, -5, -6, -3, -2, -4],\n'
        '[-1, -1, -1, -1, -1, -1, -1, -1],\n'
        '[0, 0, 0, 0, 0, 0, 0, 0],\n'
        '[0, 0, 0, 0, 0, 0, 0, 0],\n'
        '[0, 0, 0, 0, 0, 0, 0, 0],\n'
        '[0, 0, 0, 0, 0, 0, 0, 0],\n'
        '[1, 1, 1, 1, 1, 1, 1, 1],\n'
        '[4, 2, 3, 5, 6, 3, 2, 4]]\n\n'
        'Ensure that your output strictly follows this matrix format with no '
        'deviations, based on the pieces shown in the image.'
    ),
    qa=(
        'Chess is a strategy game played on an 8x8 board with 64 squares, '
        'using six types of pieces: pawns, knights, bishops, rooks, queens, '
        'and kings, for both white and black players. The board uses a '
        'coordinate system where columns are labeled "a" through "h" from '
        'left to right, and rows are labeled "1" through "8" from bottom to '
        'top (a1 at bottom-left, h8 at top-right). Please answer the '
        'following question based on the provided screenshot of the current '
        'game state:\n'
        '{question}\n'
        'Answer: <answer>\n'
        'where <answer> should be one of A, B, C, or D.'
    ),
    rule=(
        'Chess is played on an 8x8 board following standard chess rules. Each '
        'piece moves according to its unique capabilities. The board uses '
        'algebraic coordinates with files labeled "a" through "h" from left '
        'to right and ranks labeled "1" through "8" from bottom to top (a1 at '
        'bottom-left, h8 at top-right). White moves first, followed by Black. '
        'Based on the current board state image, please choose one legal move '
        'for White and output it using Standard Algebraic Notation (SAN). For '
        'example, if White’s pawn on e2 can move to e4, your answer should be '
        '"e4"; if White’s knight on g1 can move to f3, your answer should be '
        '"Nf3".\nPlease strictly follow the following format:\n'
        'Movement: <move>\n'
        'where <move> is the move in SAN (e.g., "e4", "Nf3", "O-O").'
    )
)

player_first = True
user_is_white = True
qa = ChessQuestionAnswering
