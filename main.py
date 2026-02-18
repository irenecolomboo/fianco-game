import pygame
from board import Board
from ai import negamax, iterative_deepening_negamax
import time

pygame.init()
WINDOW_SIZE = (9 * 60 + 200, 9 * 60 + 100)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Fianco")

title_font = pygame.font.SysFont("Verdana", 48, bold=True)
text_font = pygame.font.SysFont("Arial Rounded", 28)
log_font = pygame.font.SysFont("Arial Rounded", 20)

def player_selection():
    window.fill((255, 255, 255)) 
    small_font = pygame.font.SysFont("Arial Rounded", 36)
    text = small_font.render("Press W to play as White, B to play as Black", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    window.blit(text, text_rect)
    pygame.display.update()

    selecting = True
    player1 = None
    ai_player = None
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player1 = 'W'
                    ai_player = 'B'
                    selecting = False
                elif event.key == pygame.K_b:
                    player1 = 'B'
                    ai_player = 'W'
                    selecting = False
    return player1, ai_player

player1, ai_player = player_selection()
board = Board()
board.current_player = 'W'

running = True
game_over = False
ai_playing = False
winner = None
total_ai_time = 0.0  
last_move_time = 0.0  

def print_history(window):
    log_start_x = 9 * 60 + 20
    log_start_y = 50

    for i, move in enumerate(board.move_log[-10:]):
        text = log_font.render(move, True, (0, 0, 0))
        window.blit(text, (log_start_x, log_start_y + i * 25))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and board.current_player == player1 and not game_over:
            x, y = pygame.mouse.get_pos()
            if 50 <= y <= 50 + 9 * 60 and 0 <= x <= 9 * 60:
                row = (y - 50) // 60
                col = x // 60

                if board.selected_piece:
                    valid_moves, is_capture = board.get_valid_moves(board.selected_piece)
                    if (row, col) in valid_moves:
                        board.move_piece(board.selected_piece, (row, col))
                        board.current_player = ai_player
                        board.selected_piece = None
                        winner = board.check_winner()
                        if winner:
                            game_over = True
                    else:
                        board.selected_piece = None
                elif board.board[row][col] == board.current_player:
                    board.selected_piece = (row, col)
                    board.valid_moves, is_capture = board.get_valid_moves(board.selected_piece)
                    if is_capture:
                        board.valid_moves = [move for move in board.valid_moves if abs(move[0] - move[1]) > 1]

    if board.current_player == ai_player and not ai_playing and not game_over:
        ai_playing = True
        start_time = time.time()

        best_move = iterative_deepening_negamax(board, max_depth=11, player=board.current_player, time_limit=10.0)

        end_time = time.time()
        last_move_time = end_time - start_time
        total_ai_time += last_move_time

        if best_move:
            from_pos, to_pos = best_move
            board.move_piece(from_pos, to_pos)
            board.current_player = player1
            winner = board.check_winner()
            if winner:
                game_over = True

        ai_playing = False

    window.fill((255, 255, 255))
    board.draw_board(window)
    board.draw_pieces(window)
    print_history(window)

    if board.selected_piece:
        board.draw_possible_moves(window)

    ai_time_text = text_font.render(f"AI Thinking Time: {total_ai_time:.2f}s (+{last_move_time:.2f}s)", True, (0, 0, 0))
    window.blit(ai_time_text, (10, WINDOW_SIZE[1] - 40))

    if game_over and winner:
        winner_text = title_font.render(winner, True, (255, 0, 0))
        text_rect = winner_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        window.blit(winner_text, text_rect)

    pygame.display.flip()

pygame.quit()
