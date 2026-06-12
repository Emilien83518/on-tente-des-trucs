import pygame
import sys
from game import Game

# --- Constants ---
WINDOW_SIZE = 640       # The window will be 640x640 pixels
SQUARE_SIZE = WINDOW_SIZE // 8  # Each square is 80x80 pixels

# Colors used to draw the board
LIGHT_SQUARE = (240, 217, 181)   # Beige — light squares
DARK_SQUARE  = (181, 136, 99)    # Brown — dark squares
HIGHLIGHT    = (186, 202, 68)    # Yellow-green — selected piece
VALID_MOVE   = (100, 200, 100)   # Green — valid move destination
WHITE_COLOR  = (255, 255, 255)
BLACK_COLOR  = (0, 0, 0)


class ChessInterface:
    # Manages the Pygame window and everything the player sees and clicks on

    def __init__(self):
        # Sets up the window, fonts, and the game logic
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess Game")

        self.font = pygame.font.SysFont("segoeuisymbol", 52)  # Font used to draw the piece symbols
        self.small_font = pygame.font.SysFont("arial", 16)    # Font for board coordinates (a-h, 1-8)

        self.game = Game()

        self.selected_pos = None    # The square the player clicked on (row, col), or None
        self.valid_moves = []       # List of squares the selected piece can move to

    def get_square_from_mouse(self, mouse_x, mouse_y):
        # Converts a mouse click position (pixels) into a board square (row, col)
        # mouse_x: horizontal pixel position
        # mouse_y: vertical pixel position
        # Returns: (row, col) tuple
        col = mouse_x // SQUARE_SIZE
        row = mouse_y // SQUARE_SIZE
        return (row, col)

    def draw_board(self):
        # Draws the 8x8 chessboard with alternating light and dark squares
        for row in range(8):
            for col in range(8):
                # Determine the square color based on its position
                if (row + col) % 2 == 0:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE

                # Highlight the selected square
                if self.selected_pos == (row, col):
                    color = HIGHLIGHT

                # Highlight valid move destinations
                if (row, col) in self.valid_moves:
                    color = VALID_MOVE

                # Draw the square
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )

    def draw_coordinates(self):
        # Draws the column letters (a-h) and row numbers (1-8) around the board
        columns = "abcdefgh"
        for i in range(8):
            # Column letters along the bottom
            letter = self.small_font.render(columns[i], True, BLACK_COLOR)
            self.screen.blit(letter, (i * SQUARE_SIZE + SQUARE_SIZE - 16, WINDOW_SIZE - 18))

            # Row numbers along the left side
            number = self.small_font.render(str(8 - i), True, BLACK_COLOR)
            self.screen.blit(number, (2, i * SQUARE_SIZE + 2))

    def get_piece_symbol(self, piece):
        # Returns the Unicode chess symbol for a given piece so we can draw it on the board
        # Each piece has a white version (hollow) and a black version (filled)
        symbols = {
            ("King",   "white"): "♔",
            ("Queen",  "white"): "♕",
            ("Rook",   "white"): "♖",
            ("Bishop", "white"): "♗",
            ("Knight", "white"): "♘",
            ("Pawn",   "white"): "♙",
            ("King",   "black"): "♚",
            ("Queen",  "black"): "♛",
            ("Rook",   "black"): "♜",
            ("Bishop", "black"): "♝",
            ("Knight", "black"): "♞",
            ("Pawn",   "black"): "♟",
        }
        return symbols.get((piece.name, piece.color), "?")

    def draw_pieces(self):
        # Draws each piece on its square using Unicode chess symbols
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece is not None:
                    symbol = self.get_piece_symbol(piece)
                    text = self.font.render(symbol, True, BLACK_COLOR)

                    # Center the symbol inside the square
                    x = col * SQUARE_SIZE + (SQUARE_SIZE - text.get_width()) // 2
                    y = row * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
                    self.screen.blit(text, (x, y))

    def draw_status_bar(self):
        # Draws a small status message at the top of the screen showing whose turn it is
        turn_text = f"{'WHITE' if self.game.current_turn == 'white' else 'BLACK'}'s turn"
        if self.game.game_over:
            turn_text = f"GAME OVER — {self.game.winner.upper()} WINS!"

        # Draw a background bar
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, WINDOW_SIZE, 24))
        label = self.small_font.render(turn_text, True, WHITE_COLOR)
        self.screen.blit(label, (10, 4))

    def handle_click(self, row, col):
        # Handles what happens when the player clicks on a square
        # If no piece is selected yet, try to select the clicked piece
        # If a piece is already selected, try to move it to the clicked square

        if self.selected_pos is None:
            # Try to select a piece
            piece = self.game.board.get_piece(row, col)
            if piece is not None and piece.color == self.game.current_turn:
                self.selected_pos = (row, col)
                self.valid_moves = piece.get_valid_moves(self.game.board.grid)
        else:
            if (row, col) in self.valid_moves:
                # Build a move string like "e2 e4" and send it to the game
                col_letters = "abcdefgh"
                from_row, from_col = self.selected_pos
                from_str = f"{col_letters[from_col]}{8 - from_row}"
                to_str   = f"{col_letters[col]}{8 - row}"
                self.game.play_move(f"{from_str} {to_str}")

            # Deselect regardless of whether the move was valid
            self.selected_pos = None
            self.valid_moves = []

    def run(self):
        # The main game loop — keeps the window open and responds to player input
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Player closed the window
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and not self.game.game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    row, col = self.get_square_from_mouse(mouse_x, mouse_y)
                    self.handle_click(row, col)

            # Draw everything
            self.draw_board()
            self.draw_pieces()
            self.draw_coordinates()
            self.draw_status_bar()

            pygame.display.flip()   # Refresh the screen
            clock.tick(60)          # Run at 60 frames per second


if __name__ == "__main__":
    # Start the game when this file is run directly
    ChessInterface().run()
