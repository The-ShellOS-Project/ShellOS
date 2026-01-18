import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game state
board = [["" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
bot_turn = True

# Pygame screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe (Bot vs Player)")
screen.fill(WHITE)

# Draw the grid
def draw_grid():
    for row in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (row * CELL_SIZE, 0), (row * CELL_SIZE, HEIGHT), LINE_WIDTH)

# Draw X and O
def draw_xo():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == "X":
                pygame.draw.line(screen, RED, (col * CELL_SIZE + 20, row * CELL_SIZE + 20),
                                 ((col + 1) * CELL_SIZE - 20, (row + 1) * CELL_SIZE - 20), LINE_WIDTH)
                pygame.draw.line(screen, RED, ((col + 1) * CELL_SIZE - 20, row * CELL_SIZE + 20),
                                 (col * CELL_SIZE + 20, (row + 1) * CELL_SIZE - 20), LINE_WIDTH)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, BLACK, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2),
                                   CELL_SIZE // 3, LINE_WIDTH)

# Check for a win or a draw
def check_winner():
    # Rows and columns
    for row in range(GRID_SIZE):
        if board[row][0] == board[row][1] == board[row][2] != "":
            return board[row][0]
        if board[0][row] == board[1][row] == board[2][row] != "":
            return board[0][row]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    # Check for draw
    for row in board:
        if "" in row:
            return None
    return "Draw"

# Bot move
def bot_move():
    empty_cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE) if board[row][col] == ""]
    if empty_cells:
        row, col = random.choice(empty_cells)
        board[row][col] = "X"

# Game loop
def main():
    global bot_turn
    running = True
    while running:
        screen.fill(WHITE)
        draw_grid()
        draw_xo()
        pygame.display.flip()

        winner = check_winner()
        if winner:
            print(f"{winner} wins!" if winner != "Draw" else "It's a draw!")
            pygame.time.wait(2000)
            running = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not bot_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if board[row][col] == "":
                    board[row][col] = "O"
                    bot_turn = True

        if bot_turn:
            bot_move()
            bot_turn = False

if __name__ == "__main__":
    main()
