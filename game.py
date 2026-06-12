import copy
from board import Board
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight


class Game:
    # Manages the overall chess game — turns, check rules, castling, and pawn promotion

    def __init__(self):
        # Sets up a fresh game with a new board and gives the first turn to white
        self.board = Board()
        self.current_turn = "white"
        self.game_over = False
        self.winner = None
        self.status = ""           # Extra message e.g. "Check!" shown in the interface
        self.pending_promotion = None  # Holds (row, col) of a pawn waiting to be promoted

    def switch_turn(self):
        # Switches the active player from white to black or vice versa
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def opponent_of(self, color):
        # Returns the opposite color
        # color: "white" or "black"
        return "black" if color == "white" else "white"

    def find_king(self, color, grid):
        # Finds the position of the king of a given color on the board
        # color: "white" or "black"
        # grid: the 8x8 grid to search in
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
        # by_color: the attacking side ("white" or "black")
        # grid: the board to use
        # Returns: True if the square is under attack
        for r in range(8):
            for c in range(8):
                piece = grid[r][c]
                if piece is not None and piece.color == by_color:
                    if (row, col) in piece.get_valid_moves(grid):
                        return True
        return False

    def is_in_check(self, color, grid):
        # Checks whether the king of a given color is currently in check
        # color: "white" or "black"
        # grid: the board to use
        # Returns: True if the king is in check
        king_pos = self.find_king(color, grid)
        if king_pos is None:
            return False
        row, col = king_pos
        return self.is_square_attacked(row, col, self.opponent_of(color), grid)

    def simulate_move(self, grid, from_pos, to_pos):
        # Returns a copy of the board with the move applied, without touching the real game
        # Used to test whether a move would leave the king in check
        # from_pos: (row, col) of the piece to move
        # to_pos: (row, col) of the destination
        new_grid = copy.deepcopy(grid)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = new_grid[from_row][from_col]
        new_grid[to_row][to_col] = piece
        new_grid[from_row][from_col] = None
        if piece is not None:
            piece.position = to_pos
        return new_grid

    def is_castling_move(self, piece, from_pos, to_pos):
        # Returns True if this move is a castling move (king moving 2 squares sideways)
        # piece: the piece being moved
        # from_pos: starting position
        # to_pos: destination position
        if piece.name != "King":
            return False
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        return from_row == to_row and abs(to_col - from_col) == 2

    def get_legal_moves(self, piece, from_pos, grid):
        # Returns only the truly legal moves for a piece —
        # filtering out any move that leaves the king in check
        # For castling, also ensures the king does not pass through check
        # piece: the piece to get moves for
        # from_pos: (row, col) of that piece
        # grid: the current board state
        # Returns: list of (row, col) positions the piece can legally move to
        raw_moves = piece.get_valid_moves(grid)
        legal = []

        for to_pos in raw_moves:
            if self.is_castling_move(piece, from_pos, to_pos):
                # For castling, the king must not be in check now,
                # and must not pass through a square that is under attack
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                direction = 1 if to_col > from_col else -1
                passing_col = from_col + direction  # The square the king passes through

                opponent = self.opponent_of(piece.color)
                currently_in_check = self.is_square_attacked(from_row, from_col, opponent, grid)
                passes_through_check = self.is_square_attacked(from_row, passing_col, opponent, grid)
                lands_in_check = self.is_square_attacked(to_row, to_col, opponent, grid)

                if not currently_in_check and not passes_through_check and not lands_in_check:
                    legal.append(to_pos)
            else:
                simulated = self.simulate_move(grid, from_pos, to_pos)
                if not self.is_in_check(piece.color, simulated):
                    legal.append(to_pos)

        return legal

    def has_any_legal_move(self, color, grid):
        # Returns True if the given player has at least one legal move available
        # color: "white" or "black"
        # grid: the current board state
        for row in range(8):
            for col in range(8):
                piece = grid[row][col]
                if piece is not None and piece.color == color:
                    if self.get_legal_moves(piece, (row, col), grid):
                        return True
        return False

    def apply_castling(self, from_pos, to_pos):
        # Moves the rook to its correct square when the king castles
        # Called after the king has already been moved
        # from_pos: where the king started
        # to_pos: where the king landed
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if to_col == 6:
            # Kingside — rook goes from col 7 to col 5
            rook = self.board.grid[from_row][7]
            self.board.grid[from_row][5] = rook
            self.board.grid[from_row][7] = None
            if rook:
                rook.position = (from_row, 5)
                rook.has_moved = True
        elif to_col == 2:
            # Queenside — rook goes from col 0 to col 3
            rook = self.board.grid[from_row][0]
            self.board.grid[from_row][3] = rook
            self.board.grid[from_row][0] = None
            if rook:
                rook.position = (from_row, 3)
                rook.has_moved = True

    def promote_pawn(self, row, col, choice):
        # Replaces a pawn that reached the last rank with the chosen piece
        # row, col: position of the pawn to promote
        # choice: one of "queen", "rook", "bishop", "knight"
        color = self.board.grid[row][col].color
        pieces_map = {
            "queen":  Queen(color, (row, col)),
            "rook":   Rook(color, (row, col)),
            "bishop": Bishop(color, (row, col)),
            "knight": Knight(color, (row, col)),
        }
        new_piece = pieces_map.get(choice, Queen(color, (row, col)))
        self.board.grid[row][col] = new_piece
        self.pending_promotion = None

        # After promotion, check game state for the opponent
        self.switch_turn()
        self._check_game_state()

    def _check_game_state(self):
        # After each move, evaluates whether the next player is in check, checkmate, or stalemate
        # Updates self.game_over, self.winner, and self.status accordingly
        opponent = self.current_turn
        in_check  = self.is_in_check(opponent, self.board.grid)
        has_moves = self.has_any_legal_move(opponent, self.board.grid)

        if in_check and not has_moves:
            self.game_over = True
            self.winner = self.opponent_of(opponent)
            self.status = "Checkmate!"
        elif not in_check and not has_moves:
            self.game_over = True
            self.winner = None
            self.status = "Stalemate — Draw!"
        elif in_check:
            self.status = "Check!"
        else:
            self.status = ""

    def parse_move(self, move_str):
        # Converts a move string like "e2 e4" into board coordinates
        # move_str: "a1 b2" format — letter = column, number = row
        # Returns: ((from_row, from_col), (to_row, to_col)) or None if invalid
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
        # Tries to apply a move given as "e2 e4"
        # Handles castling and triggers pawn promotion if needed
        # Returns a message explaining the result
        if self.pending_promotion:
            return "Please choose a piece to promote your pawn to first."

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

        legal_moves = self.get_legal_moves(piece, from_pos, self.board.grid)
        if to_pos not in legal_moves:
            if to_pos in piece.get_valid_moves(self.board.grid):
                return "You cannot move there — your king would be in check."
            return "Invalid move for that piece."

        # Check if this is a castling move before applying it
        castling = self.is_castling_move(piece, from_pos, to_pos)

        # Apply the move
        self.board.move_piece(from_pos, to_pos)

        # If the king castled, also move the rook
        if castling:
            self.apply_castling(from_pos, to_pos)

        # Check if a pawn reached the last rank and needs promotion
        to_row, to_col = to_pos
        moved_piece = self.board.get_piece(to_row, to_col)
        if moved_piece and moved_piece.name == "Pawn" and moved_piece.is_promotion():
            self.pending_promotion = (to_row, to_col)
            return "Pawn promotion! Choose a piece: queen, rook, bishop, or knight."

        # Switch turn and evaluate game state
        self.switch_turn()
        self._check_game_state()

        if self.game_over:
            return f"{self.status} {self.winner.upper() + ' wins!' if self.winner else 'Draw!'}"
        if self.status == "Check!":
            return f"Move accepted. {self.current_turn.upper()} is in CHECK!"
        return f"Move accepted. It is now {self.current_turn}'s turn."

    def get_board_display(self):
        # Returns the board as a printable string — used by the terminal/network mode
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        self.board.display()
        sys.stdout = old_stdout
        return buffer.getvalue()
