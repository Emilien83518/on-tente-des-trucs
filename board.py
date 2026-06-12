from pieces.king import King
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.pawn import Pawn


class Board:
    # Represents the chess board
    # The board is an 8x8 grid where each cell contains either a piece or None (empty)
    # Rows and columns are numbered 0 to 7
    # Row 0 is the top of the board (black's back rank), row 7 is the bottom (white's back rank)

    def __init__(self):
        # Creates the board and places all pieces in their starting positions
        self.grid = self._create_empty_grid()
        self._place_pieces()

    def _create_empty_grid(self):
        # Creates an 8x8 grid filled with None — meaning every square starts empty
        return [[None for _ in range(8)] for _ in range(8)]

    def _place_pieces(self):
        # Places all pieces on the board in their standard chess starting positions

        # --- Black pieces (top of the board, rows 0 and 1) ---
        self.grid[0][0] = Rook("black", (0, 0))
        self.grid[0][1] = Knight("black", (0, 1))
        self.grid[0][2] = Bishop("black", (0, 2))
        self.grid[0][3] = Queen("black", (0, 3))
        self.grid[0][4] = King("black", (0, 4))
        self.grid[0][5] = Bishop("black", (0, 5))
        self.grid[0][6] = Knight("black", (0, 6))
        self.grid[0][7] = Rook("black", (0, 7))

        # Black pawns fill the entire second row
        for col in range(8):
            self.grid[1][col] = Pawn("black", (1, col))

        # --- White pieces (bottom of the board, rows 6 and 7) ---
        self.grid[7][0] = Rook("white", (7, 0))
        self.grid[7][1] = Knight("white", (7, 1))
        self.grid[7][2] = Bishop("white", (7, 2))
        self.grid[7][3] = Queen("white", (7, 3))
        self.grid[7][4] = King("white", (7, 4))
        self.grid[7][5] = Bishop("white", (7, 5))
        self.grid[7][6] = Knight("white", (7, 6))
        self.grid[7][7] = Rook("white", (7, 7))

        # White pawns fill the entire seventh row
        for col in range(8):
            self.grid[6][col] = Pawn("white", (6, col))

    def get_piece(self, row, col):
        # Returns the piece at a given position, or None if the square is empty
        return self.grid[row][col]

    def move_piece(self, from_pos, to_pos):
        # Moves a piece from one square to another
        # from_pos: (row, col) of the piece to move
        # to_pos: (row, col) of the destination square
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece = self.grid[from_row][from_col]

        if piece is None:
            # No piece at the starting position — nothing to move
            return False

        valid_moves = piece.get_valid_moves(self.grid)

        if to_pos not in valid_moves:
            # The destination is not a legal move for this piece
            return False

        # Place the piece on the destination square
        self.grid[to_row][to_col] = piece

        # Clear the original square
        self.grid[from_row][from_col] = None

        # Update the piece's internal position
        piece.move(to_pos)

        return True

    def display(self):
        # Prints the board in the terminal as a simple text grid
        # Useful for testing without a graphical interface
        print("  a b c d e f g h")
        print(" +" + "-+" * 8)

        for row in range(8):
            # Chess ranks go from 8 (top) to 1 (bottom)
            rank = 8 - row
            row_display = f"{rank}|"

            for col in range(8):
                piece = self.grid[row][col]
                if piece is None:
                    row_display += ".|"
                else:
                    row_display += f"{self._get_symbol(piece)}|"

            print(row_display)

        print(" +" + "-+" * 8)

    def _get_symbol(self, piece):
        # Returns a single character to represent a piece in the terminal display
        # Uppercase = white, lowercase = black
        symbols = {
            "King":   ("K", "k"),
            "Queen":  ("Q", "q"),
            "Rook":   ("R", "r"),
            "Bishop": ("B", "b"),
            "Knight": ("N", "n"),
            "Pawn":   ("P", "p"),
        }
        white_symbol, black_symbol = symbols[piece.name]
        return white_symbol if piece.color == "white" else black_symbol
