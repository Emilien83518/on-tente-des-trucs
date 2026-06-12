import copy
from board import Board
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight


class Game:
    # Manages the overall chess game — turns, check, castling, promotion, en passant, and draw rules

    def __init__(self):
        # Sets up a fresh game with all state variables initialized
        self.board = Board()
        self.current_turn = "white"
        self.game_over = False
        self.winner = None
        self.status = ""                # Message shown in the interface e.g. "Check!"
        self.pending_promotion = None   # (row, col) of a pawn waiting to be promoted

        # En passant: stores the square a pawn just skipped over with a double step
        # The opponent can capture on this square on their very next move only
        self.en_passant_target = None

        # 50-move rule: counts half-moves since the last pawn move or capture
        # If it reaches 100 (= 50 full moves), the game is declared a draw
        self.halfmove_clock = 0

        # Threefold repetition: stores a snapshot of each position after every move
        # If the same position appears 3 times, the game is a draw
        self.position_history = []
        self.position_history.append(self._board_snapshot())

    def switch_turn(self):
        # Switches the active player from white to black or vice versa
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def opponent_of(self, color):
        # Returns the opposite color
        # color: "white" or "black"
        # Returns: "black" or "white"
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

    def simulate_move(self, grid, from_pos, to_pos, en_passant_target=None):
        # Returns a copy of the board with the move applied, without touching the real game
        # Also handles en passant captures in the simulation
        # from_pos: (row, col) of the piece to move
        # to_pos: (row, col) of the destination
        # en_passant_target: the en passant square if active (may trigger pawn removal)
        new_grid = copy.deepcopy(grid)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = new_grid[from_row][from_col]
        new_grid[to_row][to_col] = piece
        new_grid[from_row][from_col] = None
        if piece is not None:
            piece.position = to_pos

        # If this move is an en passant capture, remove the captured pawn from the board
        if (piece is not None and piece.name == "Pawn"
                and en_passant_target is not None
                and to_pos == en_passant_target):
            captured_row = from_row  # The captured pawn is on the same row as the capturing pawn
            new_grid[captured_row][to_col] = None

        return new_grid

    def is_castling_move(self, piece, from_pos, to_pos):
        # Returns True if this move is a castling move (king moving 2 squares sideways)
        if piece.name != "King":
            return False
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        return from_row == to_row and abs(to_col - from_col) == 2

    def is_en_passant_move(self, piece, to_pos):
        # Returns True if this move is an en passant capture
        # piece: the piece being moved (must be a pawn)
        # to_pos: the destination square
        return (piece.name == "Pawn"
                and self.en_passant_target is not None
                and to_pos == self.en_passant_target)

    def get_legal_moves(self, piece, from_pos, grid):
        # Returns only the truly legal moves for a piece —
        # filtering out moves that leave the king in check
        # Also adds en passant as a valid move when applicable
        # piece: the piece to get moves for
        # from_pos: (row, col) of that piece
        # grid: the current board state
        # Returns: list of (row, col) positions the piece can legally move to
        raw_moves = list(piece.get_valid_moves(grid))

        # Add en passant as a possible destination for pawns
        if piece.name == "Pawn" and self.en_passant_target is not None:
            from_row, from_col = from_pos
            ep_row, ep_col = self.en_passant_target
            direction = -1 if piece.color == "white" else 1
            # The pawn can capture en passant if it is on the correct row and adjacent column
            if from_row == ep_row - direction and abs(from_col - ep_col) == 1:
                raw_moves.append(self.en_passant_target)

        legal = []
        for to_pos in raw_moves:
            if self.is_castling_move(piece, from_pos, to_pos):
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                direction = 1 if to_col > from_col else -1
                passing_col = from_col + direction
                opponent = self.opponent_of(piece.color)
                if (not self.is_square_attacked(from_row, from_col, opponent, grid)
                        and not self.is_square_attacked(from_row, passing_col, opponent, grid)
                        and not self.is_square_attacked(to_row, to_col, opponent, grid)):
                    legal.append(to_pos)
            else:
                simulated = self.simulate_move(grid, from_pos, to_pos, self.en_passant_target)
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
        # from_pos: where the king started, to_pos: where the king landed
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        if to_col == 6:
            # Kingside — rook moves from h-file (col 7) to f-file (col 5)
            rook = self.board.grid[from_row][7]
            self.board.grid[from_row][5] = rook
            self.board.grid[from_row][7] = None
            if rook:
                rook.position = (from_row, 5)
                rook.has_moved = True
        elif to_col == 2:
            # Queenside — rook moves from a-file (col 0) to d-file (col 3)
            rook = self.board.grid[from_row][0]
            self.board.grid[from_row][3] = rook
            self.board.grid[from_row][0] = None
            if rook:
                rook.position = (from_row, 3)
                rook.has_moved = True

    def promote_pawn(self, row, col, choice):
        # Replaces a pawn that reached the last rank with the chosen piece
        # row, col: position of the pawn
        # choice: "queen", "rook", "bishop", or "knight"
        color = self.board.grid[row][col].color
        pieces_map = {
            "queen":  Queen(color, (row, col)),
            "rook":   Rook(color, (row, col)),
            "bishop": Bishop(color, (row, col)),
            "knight": Knight(color, (row, col)),
        }
        self.board.grid[row][col] = pieces_map.get(choice, Queen(color, (row, col)))
        self.pending_promotion = None

        # Record position and check game state after promotion
        self.position_history.append(self._board_snapshot())
        self.switch_turn()
        self._check_game_state()

    def _board_snapshot(self):
        # Creates a compact string representation of the current board position
        # Used to detect threefold repetition — if the same snapshot appears 3 times, it's a draw
        # Returns: a string that uniquely identifies the current board state
        snapshot = ""
        for row in self.board.grid:
            for piece in row:
                if piece is None:
                    snapshot += "."
                else:
                    # Use uppercase for white, lowercase for black, first letter of piece name
                    letter = piece.name[0] if piece.name != "Knight" else "N"
                    snapshot += letter.upper() if piece.color == "white" else letter.lower()
        snapshot += self.current_turn[0]                            # Whose turn it is
        snapshot += str(self.en_passant_target)                     # En passant availability
        return snapshot

    def _check_draw_rules(self):
        # Checks the 50-move rule and threefold repetition
        # Returns a draw message if either rule applies, or None if neither does
        if self.halfmove_clock >= 100:
            return "50-move rule — Draw!"

        # Count how many times this exact position has appeared
        current = self._board_snapshot()
        if self.position_history.count(current) >= 3:
            return "Threefold repetition — Draw!"

        return None

    def _check_game_state(self):
        # Evaluates the game state after each move — check, checkmate, stalemate, or draw
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
        else:
            draw_reason = self._check_draw_rules()
            if draw_reason:
                self.game_over = True
                self.winner = None
                self.status = draw_reason
            elif in_check:
                self.status = "Check!"
            else:
                self.status = ""

    def parse_move(self, move_str):
        # Converts a move string like "e2 e4" into board coordinates
        # move_str: "a1 b2" — letter = column, number = row
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
        # Tries to apply a move, enforcing all chess rules
        # Returns a message explaining what happened
        if self.pending_promotion:
            return "Please choose a piece to promote your pawn to first."

        coords = self.parse_move(move_str)
        if coords is None:
            return "Invalid format. Use something like: e2 e4"

        from_pos, to_pos = coords
        from_row, from_col = from_pos
        to_row, to_col = to_pos

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

        castling    = self.is_castling_move(piece, from_pos, to_pos)
        en_passant  = self.is_en_passant_move(piece, to_pos)
        is_capture  = self.board.get_piece(to_row, to_col) is not None or en_passant
        is_pawn_move = piece.name == "Pawn"

        # --- Update the 50-move clock before applying the move ---
        if is_pawn_move or is_capture:
            self.halfmove_clock = 0   # Reset on pawn move or capture
        else:
            self.halfmove_clock += 1  # Increment otherwise

        # --- Apply the move ---
        self.board.move_piece(from_pos, to_pos)

        # Remove the captured pawn for en passant (it is NOT on the destination square)
        if en_passant:
            self.board.grid[from_row][to_col] = None

        # Move the rook if the king castled
        if castling:
            self.apply_castling(from_pos, to_pos)

        # --- Update the en passant target for the next move ---
        if is_pawn_move and abs(to_row - from_row) == 2:
            # Pawn just moved 2 squares — set the square it skipped as the en passant target
            skipped_row = (from_row + to_row) // 2
            self.en_passant_target = (skipped_row, to_col)
        else:
            self.en_passant_target = None  # En passant is only valid for one turn

        # --- Check for pawn promotion ---
        moved_piece = self.board.get_piece(to_row, to_col)
        if moved_piece and moved_piece.name == "Pawn" and moved_piece.is_promotion():
            self.pending_promotion = (to_row, to_col)
            return "Pawn promotion! Choose a piece: queen, rook, bishop, or knight."

        # --- Record the position and evaluate game state ---
        self.position_history.append(self._board_snapshot())
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
