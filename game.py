import copy
from board import Board


class Game:
    # Manages the overall chess game — tracks whose turn it is and enforces all check rules

    def __init__(self):
        # Sets up a fresh game with a new board and gives the first turn to white
        self.board = Board()
        self.current_turn = "white"  # White always goes first in chess
        self.game_over = False
        self.winner = None
        self.status = ""  # Extra message shown to the player e.g. "Check!"

    def switch_turn(self):
        # Switches the turn from white to black, or from black to white
        if self.current_turn == "white":
            self.current_turn = "black"
        else:
            self.current_turn = "white"

    def opponent_of(self, color):
        # Returns the opposite color
        # color: "white" or "black"
        # Returns: "black" or "white"
        return "black" if color == "white" else "white"

    def find_king(self, color, grid):
        # Finds the position of the king of a given color on the board
        # color: "white" or "black"
        # grid: the 8x8 board grid to search in
        # Returns: (row, col) of the king, or None if not found
        for row in range(8):
            for col in range(8):
                piece = grid[row][col]
                if piece is not None and piece.name == "King" and piece.color == color:
                    return (row, col)
        return None

    def is_square_attacked(self, row, col, by_color, grid):
        # Checks whether a given square is attacked by any piece of a specific color
        # row, col: the square to check
        # by_color: the color of the attacking side ("white" or "black")
        # grid: the 8x8 board to use for checking
        # Returns: True if the square is under attack, False otherwise
        for r in range(8):
            for c in range(8):
                piece = grid[r][c]
                if piece is not None and piece.color == by_color:
                    if (row, col) in piece.get_valid_moves(grid):
                        return True
        return False

    def is_in_check(self, color, grid):
        # Checks whether the king of a given color is currently in check
        # color: "white" or "black" — the side to check
        # grid: the 8x8 board to use
        # Returns: True if that king is in check, False otherwise
        king_pos = self.find_king(color, grid)
        if king_pos is None:
            return False  # King not found (should not happen in a real game)
        row, col = king_pos
        return self.is_square_attacked(row, col, self.opponent_of(color), grid)

    def simulate_move(self, grid, from_pos, to_pos):
        # Simulates a move on a copy of the board without changing the real game state
        # This lets us test whether a move would leave our own king in check
        # from_pos: (row, col) of the piece to move
        # to_pos: (row, col) of the destination square
        # Returns: a new 8x8 grid with the move applied
        new_grid = copy.deepcopy(grid)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = new_grid[from_row][from_col]
        new_grid[to_row][to_col] = piece
        new_grid[from_row][from_col] = None
        if piece is not None:
            piece.position = to_pos  # Update the piece's position on the simulated board
        return new_grid

    def get_legal_moves(self, piece, from_pos, grid):
        # Returns only the moves that are truly legal for a piece —
        # meaning they do not leave the piece's own king in check
        # piece: the piece to get moves for
        # from_pos: (row, col) where the piece currently is
        # grid: the current board state
        # Returns: a list of (row, col) positions the piece can safely move to
        raw_moves = piece.get_valid_moves(grid)
        legal = []
        for to_pos in raw_moves:
            simulated = self.simulate_move(grid, from_pos, to_pos)
            if not self.is_in_check(piece.color, simulated):
                legal.append(to_pos)
        return legal

    def has_any_legal_move(self, color, grid):
        # Checks whether a player has at least one legal move available
        # color: the player to check ("white" or "black")
        # grid: the current board state
        # Returns: True if at least one legal move exists, False otherwise
        for row in range(8):
            for col in range(8):
                piece = grid[row][col]
                if piece is not None and piece.color == color:
                    if self.get_legal_moves(piece, (row, col), grid):
                        return True
        return False

    def parse_move(self, move_str):
        # Converts a move typed by the player (like "e2 e4") into board coordinates
        # move_str: a string in the format "a1 b2" where letters are columns and numbers are rows
        # Returns: a tuple ((from_row, from_col), (to_row, to_col)) or None if the input is invalid
        try:
            parts = move_str.strip().lower().split()
            if len(parts) != 2:
                return None

            col_map = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

            from_col = col_map.get(parts[0][0])
            from_row = 8 - int(parts[0][1])
            to_col   = col_map.get(parts[1][0])
            to_row   = 8 - int(parts[1][1])

            if None in (from_col, to_col):
                return None

            return (from_row, from_col), (to_row, to_col)
        except (IndexError, ValueError):
            return None

    def play_move(self, move_str):
        # Tries to apply a move given as a string like "e2 e4"
        # Rejects the move if it leaves the king in check
        # Returns a message telling the player if the move worked or why it failed
        coords = self.parse_move(move_str)

        if coords is None:
            return "Invalid format. Use something like: e2 e4"

        from_pos, to_pos = coords
        from_row, from_col = from_pos

        piece = self.board.get_piece(from_row, from_col)

        if piece is None:
            return "No piece at that position."

        if piece.color != self.current_turn:
            return f"It is {self.current_turn}'s turn."

        # Check that this move is in the piece's legal moves (not just valid moves)
        legal_moves = self.get_legal_moves(piece, from_pos, self.board.grid)

        if to_pos not in legal_moves:
            # Give a specific reason if the move would put/leave the king in check
            if to_pos in piece.get_valid_moves(self.board.grid):
                return "You cannot move there — your king would be in check."
            return "Invalid move for that piece."

        # Apply the move on the real board
        self.board.move_piece(from_pos, to_pos)

        # Switch to the other player's turn
        self.switch_turn()

        # Check the state for the next player
        opponent = self.current_turn
        in_check = self.is_in_check(opponent, self.board.grid)
        has_moves = self.has_any_legal_move(opponent, self.board.grid)

        if in_check and not has_moves:
            # Checkmate — the opponent has no way to escape check
            self.game_over = True
            self.winner = self.opponent_of(opponent)
            self.status = "Checkmate!"
            return f"Checkmate! {self.winner.upper()} wins!"

        if not in_check and not has_moves:
            # Stalemate — the opponent has no legal move but is not in check — it's a draw
            self.game_over = True
            self.winner = None
            self.status = "Stalemate — Draw!"
            return "Stalemate! It's a draw."

        if in_check:
            self.status = "Check!"
            return f"Move accepted. {opponent.upper()} is in CHECK!"

        self.status = ""
        return f"Move accepted. It is now {self.current_turn}'s turn."

    def get_board_display(self):
        # Returns the board as a string so it can be sent over the network and printed in the terminal
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        self.board.display()
        sys.stdout = old_stdout
        return buffer.getvalue()
