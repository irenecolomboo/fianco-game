import pygame
import random
import string

pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

BOARD_SIZE = 9
CELL_SIZE = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
STONE_SIZE = CELL_SIZE // 2 - 5
BOARD_COLOR_1 = (235, 205, 158)
BOARD_COLOR_2 = (181, 136, 99)
STONE_BLACK_COLOR = (20, 20, 20)
STONE_WHITE_COLOR = (245, 245, 245)
HIGHLIGHT_COLOR = (0, 255, 0) 

class Board:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 'W'
        self.selected_piece = None
        self.valid_moves = []
        self.move_log = []

        self.zobrist_table = [[random.getrandbits(64) for _ in range(2)] for _ in range(9 * 9)]  
        self.zobrist_hash = self.initialize_zobrist_hash()

    def initialize_board(self):
        board = [['0' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for col in range(BOARD_SIZE):
            board[0][col] = 'B'
        board[1][1], board[1][7], board[2][2], board[2][6], board[3][3], board[3][5] = 'B', 'B', 'B', 'B', 'B', 'B'

        for col in range(BOARD_SIZE):
            board[8][col] = 'W'
        board[7][1], board[7][7], board[6][2], board[6][6], board[5][3], board[5][5] = 'W', 'W', 'W', 'W', 'W', 'W'

        return board
    
    def copy(self):
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        new_board.current_player = self.current_player
        new_board.move_log = self.move_log[:]
        return new_board

    def initialize_zobrist_hash(self):
        zobrist_hash = 0
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece == 'B':
                    zobrist_hash ^= self.zobrist_table[row * 9 + col][0]
                elif piece == 'W':
                    zobrist_hash ^= self.zobrist_table[row * 9 + col][1]
        return zobrist_hash

    def update_zobrist_hash(self, from_pos, to_pos, piece):
        row_from, col_from = from_pos
        row_to, col_to = to_pos

        if piece == 'B':
            self.zobrist_hash ^= self.zobrist_table[row_from * 9 + col_from][0]  
            self.zobrist_hash ^= self.zobrist_table[row_to * 9 + col_to][0]  
        elif piece == 'W':
            self.zobrist_hash ^= self.zobrist_table[row_from * 9 + col_from][1]  
            self.zobrist_hash ^= self.zobrist_table[row_to * 9 + col_to][1]  

    def move_piece(self, from_pos, to_pos, capture=False):
        row, col = from_pos
        new_row, new_col = to_pos

        self.board[new_row][new_col] = self.board[row][col]
        self.board[row][col] = '0'

        if abs(row - new_row) > 1 or abs(col - new_col) > 1:
            captured_row = (row + new_row) // 2
            captured_col = (col + new_col) // 2
            self.board[captured_row][captured_col] = '0'

        from_notation = self.coord_to_notation(from_pos)
        to_notation = self.coord_to_notation(to_pos)
        move_log = f"{'B' if self.current_player == 'B' else 'W'}: {from_notation}-{to_notation}"
        self.move_log.append(move_log)


    def draw_board(self, window):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * CELL_SIZE
                y = row * CELL_SIZE + 50

                color = BOARD_COLOR_1 if (row + col) % 2 == 0 else BOARD_COLOR_2
                pygame.draw.rect(window, color, (x, y, CELL_SIZE, CELL_SIZE))

                piece = self.board[row][col]
                if piece == 'B':
                    pygame.draw.circle(window, STONE_BLACK_COLOR,
                                    (x + CELL_SIZE // 2, y + CELL_SIZE // 2),
                                    STONE_SIZE)
                elif piece == 'W':
                    pygame.draw.circle(window, STONE_WHITE_COLOR,
                                    (x + CELL_SIZE // 2, y + CELL_SIZE // 2),
                                    STONE_SIZE)

                square_label = f"{string.ascii_lowercase[col]}{9 - row}"
                text = font.render(square_label, True, (0, 0, 0))  
                text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                window.blit(text, text_rect)

    def draw_pieces(self, window):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 'B':
                    pygame.draw.circle(window, STONE_BLACK_COLOR,
                                       (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2 + 50),
                                       STONE_SIZE)
                elif self.board[row][col] == 'W':
                    pygame.draw.circle(window, STONE_WHITE_COLOR,
                                       (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2 + 50),
                                       STONE_SIZE)

    def draw_possible_moves(self, window):
        for move in self.valid_moves:
            row, col = move
            pygame.draw.rect(window, HIGHLIGHT_COLOR, (col * CELL_SIZE, row * CELL_SIZE + 50, CELL_SIZE, CELL_SIZE), 4)

    def get_all_valid_moves(self):
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == self.current_player:
                    moves, is_capture = self.get_valid_moves((row, col))
                    all_moves.extend([((row, col), move) for move in moves])
        return all_moves

    def get_valid_moves(self, selected_piece):
        row, col = selected_piece
        valid_moves = []
        capture_moves = []

        player = self.board[row][col]
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
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and self.board[new_row][new_col] == '0':
                valid_moves.append((new_row, new_col))

        for direction in capture_directions:
            dr, dc = direction
            mid_row, mid_col = row + dr, col + dc
            end_row, end_col = row + 2 * dr, col + 2 * dc
            if 0 <= end_row < BOARD_SIZE and 0 <= end_col < BOARD_SIZE:
                if self.board[mid_row][mid_col] == opponent and self.board[end_row][end_col] == '0':
                    capture_moves.append((end_row, end_col))

        if capture_moves:
            return capture_moves, True
        return valid_moves, False

    def coord_to_notation(self, pos):
        row, col = pos
        letters = 'abcdefghi'
        return f"{letters[col]}{9 - row}"

    def check_winner(self):
        black_pieces = sum(row.count('B') for row in self.board)
        white_pieces = sum(row.count('W') for row in self.board)

        if black_pieces == 0:
            return 'White Wins!'
        elif white_pieces == 0:
            return 'Black Wins!'

        if 'B' in self.board[8]:
            return 'Black Wins!'
        elif 'W' in self.board[0]:
            return 'White Wins!'

        return None
