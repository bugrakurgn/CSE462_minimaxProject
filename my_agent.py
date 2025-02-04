#Bugra Kurgan 20210702025
import copy

MAX_DEPTH = 6  # Default max depth
ROWS, COLS = 7, 7

def evaluate_board(board):
    center_weights = [
        [3, 4, 5, 6, 5, 4, 3],
        [4, 6, 7, 8, 7, 6, 4],
        [5, 7, 9, 10, 9, 7, 5],
        [6, 8, 10, 12, 10, 8, 6],
        [5, 7, 9, 10, 9, 7, 5],
        [4, 6, 7, 8, 7, 6, 4],
        [3, 4, 5, 6, 5, 4, 3],
    ]

    ai_score = 0
    human_score = 0

    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 1:  # AI piece
                ai_score += center_weights[i][j]
            elif board[i][j] == 2:  # Human piece
                human_score += center_weights[i][j]

    ai_captures = calculate_captures(board, 1)
    human_captures = calculate_captures(board, 2)
    ai_score += len(ai_captures) * 25
    human_score += len(human_captures) * 25

    ai_vulnerable = calculate_vulnerable_positions(board, 1)
    human_vulnerable = calculate_vulnerable_positions(board, 2)
    ai_score -= len(ai_vulnerable) * 40
    human_score -= len(human_vulnerable) * 20

    ai_pieces = sum(row.count(1) for row in board)
    human_pieces = sum(row.count(2) for row in board)
    ai_score += (ai_pieces - human_pieces) * 15

    return ai_score - human_score



def dynamic_depth(count):
    if count < 10:  # Early game
        return 5
    elif count < 25:  # Mid game
        return 6
    else:  # Late game
        return 8


def is_piece_vulnerable(board, row, col, player):
    opponent = 3 - player

    if col > 0 and col < COLS - 1:
        if board[row][col - 1] == opponent and board[row][col + 1] == opponent:
            return True
    if row > 0 and row < ROWS - 1:
        if board[row - 1][col] == opponent and board[row + 1][col] == opponent:
            return True
    if row > 0 and row < ROWS - 1 and col > 0 and col < COLS - 1:
        if board[row - 1][col - 1] == opponent and board[row + 1][col + 1] == opponent:
            return True
    if row > 0 and row < ROWS - 1 and col > 0 and col < COLS - 1:
        if board[row - 1][col + 1] == opponent and board[row + 1][col - 1] == opponent:
            return True
    return False

def calculate_vulnerable_positions(board, player):
    vulnerable_positions = []

    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == player and is_piece_vulnerable(board, i, j, player):
                vulnerable_positions.append((i, j))

    return vulnerable_positions



def get_valid_moves(board, player):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == player:
                for d_row, d_col in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    new_row, new_col = i + d_row, j + d_col
                    if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]) and board[new_row][new_col] == 0:
                        moves.append(((i, j), (new_row, new_col)))
    return moves


def apply_move(board, move):
    new_board = copy.deepcopy(board)
    (start_row, start_col), (end_row, end_col) = move
    new_board[end_row][end_col] = new_board[start_row][start_col]
    new_board[start_row][start_col] = 0
    return new_board


def calculate_captures(board, player):
    opponent = 3 - player
    captures = []

    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == opponent:
                if j > 0 and j < COLS - 1:
                    if board[i][j - 1] == player and board[i][j + 1] == player:
                        captures.append((i, j))
                if i > 0 and i < ROWS - 1:
                    if board[i - 1][j] == player and board[i + 1][j] == player:
                        captures.append((i, j))
                if i > 0 and i < ROWS - 1 and j > 0 and j < COLS - 1:
                    if board[i - 1][j - 1] == player and board[i + 1][j + 1] == player:
                        captures.append((i, j))
                if i > 0 and i < ROWS - 1 and j > 0 and j < COLS - 1:
                    if board[i - 1][j + 1] == player and board[i + 1][j - 1] == player:
                        captures.append((i, j))
    return captures

def minimax(board, depth, max_depth, maximizing_player, alpha, beta, moved_pieces=None, total_moves=0):
    if depth == max_depth or is_game_over(board, total_moves):
        return evaluate_board(board), None

    valid_moves = get_valid_moves(board, 1 if maximizing_player else 2)
    if moved_pieces:
        valid_moves = [move for move in valid_moves if move[0] not in moved_pieces]

    if maximizing_player:
        valid_moves = [
            move for move in valid_moves
            if not is_piece_vulnerable(apply_move(board, move), move[1][0], move[1][1], 2)
        ]

    if not valid_moves:
        return evaluate_board(board), None

    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = apply_move(board, move)
            eval_score, _ = minimax(new_board, depth + 1, max_depth, False, alpha, beta, moved_pieces, total_moves + 1)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = apply_move(board, move)
            eval_score, _ = minimax(new_board, depth + 1, max_depth, True, alpha, beta, moved_pieces, total_moves + 1)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def is_game_over(board, total_moves):

    ai_pieces = sum(row.count(1) for row in board)
    human_pieces = sum(row.count(2) for row in board)

    if ai_pieces == 0:
        return True  # Human wins
    if human_pieces == 0:
        return True  # AI wins
    if total_moves >= 50:
        return True
    return False