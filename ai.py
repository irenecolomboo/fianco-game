import time

transposition_table = {}
killer_moves = {}
history_table = {}

def negamax(board, depth, player, alpha, beta, start_time, time_limit):
    if time.time() - start_time > time_limit:
        return None, None

    board_key = board.zobrist_hash
    if board_key in transposition_table:
        stored_depth, stored_eval, stored_move = transposition_table[board_key]
        if stored_depth >= depth:
            return stored_eval, stored_move

    if depth == 0:
        return quiescence_search(board, player, alpha, beta), None

    best_move = None
    max_eval = float('-inf')

    valid_moves = []
    capture_moves = []

    for row in range(9):
        for col in range(9):
            if board.board[row][col] == player:
                moves, is_capture = board.get_valid_moves((row, col))
                if is_capture:
                    capture_moves.extend([((row, col), move) for move in moves])
                else:
                    valid_moves.extend([((row, col), move) for move in moves])

    if capture_moves:
        valid_moves = capture_moves

    if not valid_moves:
        eval = evaluate_board(board.board, player)
        transposition_table[board_key] = (depth, eval, None)
        return eval, None

    valid_moves = prioritize_moves(valid_moves, depth)

    for move in valid_moves:
        from_pos, to_pos = move
        is_capture = abs(from_pos[0] - to_pos[0]) > 1

        new_board = board.copy()
        new_board.move_piece(from_pos, to_pos, capture=is_capture)

        opponent = 'W' if player == 'B' else 'B'
        eval, _ = negamax(new_board, depth - 1, opponent, -beta, -alpha, start_time, time_limit)

        if eval is None:
            return None, best_move

        eval = -eval 

        if eval > max_eval:
            max_eval = eval
            best_move = move

        alpha = max(alpha, eval)
        if alpha >= beta:
            update_history_table(move, depth)
            store_killer_move(depth, move)
            break

    transposition_table[board_key] = (depth, max_eval, best_move)

    return max_eval, best_move


def initialize_killer_moves(max_depth):
    global killer_moves
    for d in range(max_depth):
        killer_moves[d] = [None, None]

def store_killer_move(depth, move):
    if killer_moves[depth][0] is None:
        killer_moves[depth][0] = move
    elif killer_moves[depth][0] != move:
        killer_moves[depth][1] = move  

def reset_killer_moves():
    for depth in killer_moves:
        killer_moves[depth] = [None, None]

def prioritize_moves(valid_moves, depth):
    def move_priority(move):
        if move in killer_moves.get(depth, []):
            return float('inf')  
        return history_table.get(move, 0) 

    return sorted(valid_moves, key=move_priority, reverse=True)

def initialize_history_table():
    global history_table
    history_table = {}

def update_history_table(move, depth):
    if move not in history_table:
        history_table[move] = 0
    history_table[move] += depth ** 2


def get_move_score(move):
    return history_table.get(move, 0)

def sort_moves_by_history(moves):
    return sorted(moves, key=lambda move: get_move_score(move), reverse=True)


def iterative_deepening_negamax(board, max_depth, player, time_limit):
    start_time = time.time()
    best_move = None

    initialize_killer_moves(max_depth)

    for depth in range(1, max_depth + 1):
        print(f"Searching at depth {depth}...")
        max_eval, move = negamax(board, depth, player, alpha=float('-inf'), beta=float('inf'),
                                 start_time=start_time, time_limit=time_limit)
        if max_eval is None:
            print(f"Time limit exceeded at depth {depth}. Returning best move so far.")
            break
        best_move = move 
        print(f"Best move found at depth {depth}: {best_move}")

    return best_move


def evaluate_board(board, player):
    score = 0
    opponent = 'W' if player == 'B' else 'B'

    player_pieces = sum(row.count(player) for row in board)
    opponent_pieces = sum(row.count(opponent) for row in board)
    score += (player_pieces - opponent_pieces) * 100

    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == player:
                if player == 'B':
                    score += row * 10
                else:
                    score += (len(board) - 1 - row) * 10
    return score


def board_to_key(board):
    return str(board)


def get_valid_moves(board, selected_piece, player):
    row, col = selected_piece
    valid_moves = []
    capture_moves = []

    if player == 'B':
        directions = [(1, 0), (0, 1), (0, -1)]
        capture_directions = [(1, 1), (1, -1)]
        opponent = 'W'
    else:
        directions = [(-1, 0), (0, 1), (0, -1)]
        capture_directions = [(-1, 1), (-1, -1)]
        opponent = 'B'

    for direction in directions:
        dr, dc = direction
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]) and board[new_row][new_col] == '0':
            valid_moves.append((new_row, new_col))

    for direction in capture_directions:
        dr, dc = direction
        mid_row, mid_col = row + dr, col + dc
        end_row, end_col = row + 2 * dr, col + 2 * dc
        if 0 <= end_row < len(board) and 0 <= end_col < len(board[0]):
            if board[mid_row][mid_col] == opponent and board[end_row][end_col] == '0':
                capture_moves.append((end_row, end_col))

    if capture_moves:
        return capture_moves, True

    return valid_moves, False


def move_piece(board, from_pos, to_pos, capture=False):
    row_from, col_from = from_pos
    row_to, col_to = to_pos
    board[row_to][col_to] = board[row_from][col_from]
    board[row_from][col_from] = '0'

    if capture:
        captured_row = (row_from + row_to) // 2
        captured_col = (col_from + col_to) // 2
        board[captured_row][captured_col] = '0'


def check_winner(board):
    black_pieces = sum(row.count('B') for row in board)
    white_pieces = sum(row.count('W') for row in board)

    if black_pieces == 0:
        return 'White Wins!'
    elif white_pieces == 0:
        return 'Black Wins!'

    if 'B' in board[8]:
        return 'Black Wins!'
    
    if 'W' in board[0]:
        return 'White Wins!'

    return None

def quiescence_search(board, player, alpha, beta):
    stand_pat = evaluate_board(board.board, player) 

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    valid_moves = []
    for row in range(9):
        for col in range(9):
            if board.board[row][col] == player:
                moves, is_capture = board.get_valid_moves((row, col))
                if is_capture:
                    valid_moves.extend([((row, col), move) for move in moves])

    for move in valid_moves:
        from_pos, to_pos = move
        is_capture = abs(from_pos[0] - to_pos[0]) > 1

        new_board = board.copy()
        new_board.move_piece(from_pos, to_pos, capture=is_capture)

        opponent = 'W' if player == 'B' else 'B'
        score = -quiescence_search(new_board, opponent, -beta, -alpha)

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha
