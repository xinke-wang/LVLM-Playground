display = False
save_path = 'experiments/game_history'
maximum_trials = 3
device = 'cuda:0'
make_video = True

benchmark_setting = dict(
    games=['tictactoe', 'gomoku', 'minesweeper', 'reversi', 'sudoku', 'chess'],
    sample_size=2000,
    e2e_round=100,
    offline_task=['perceive', 'qa', 'rule'],
    benchmark_path='benchmark'
)
