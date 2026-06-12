class King:
    # Represents the King piece in a chess game
    # The king moves 1 square in any direction, and can also castle with a rook

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the king is on the board
        self.color = color
        self.position = position
        self.name = "King"
        self.has_moved = False  # Tracks if the king has moved (needed for castling)

    def get_valid_moves(self, board):
        # Returns all squares the king can move to, including castling squares
        # Castling check-safety is enforced in game.py via get_legal_moves
        moves = []

        directions = [
            (-1,  0), ( 1,  0), ( 0, -1), ( 0,  1),
            (-1, -1), (-1,  1), ( 1, -1), ( 1,  1),
        ]

        row, col = self.position

        # Standard one-square moves
        for row_step, col_step in directions:
            new_row = row + row_step
            new_col = col + col_step
            if self._is_on_board(new_row, new_col):
                target = board[new_row][new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))

        # --- Castling ---
        # The king must not have moved, and we check both sides
        if not self.has_moved:
            moves += self._get_castling_moves(board, row, col)

        return moves

    def _get_castling_moves(self, board, row, col):
        # Returns castling destination squares if castling is possible
        # Castling rules checked here: pieces between king and rook must be empty,
        # and the rook must not have moved. Check-safety is verified in game.py.
        castling_moves = []

        # Kingside castling (rook on the right, col 7)
        rook_ks = board[row][7]
        if (rook_ks is not None and rook_ks.name == "Rook"
                and rook_ks.color == self.color and not rook_ks.has_moved
                and board[row][5] is None and board[row][6] is None):
            # King slides to col 6 (g-file)
            castling_moves.append((row, 6))

        # Queenside castling (rook on the left, col 0)
        rook_qs = board[row][0]
        if (rook_qs is not None and rook_qs.name == "Rook"
                and rook_qs.color == self.color and not rook_qs.has_moved
                and board[row][1] is None and board[row][2] is None and board[row][3] is None):
            # King slides to col 2 (c-file)
            castling_moves.append((row, 2))

        return castling_moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the king to a new position and marks that he has moved
        self.position = new_position
        self.has_moved = True

    def __repr__(self):
        # Returns a readable string describing the king — useful for debugging
        return f"{self.color.capitalize()} King at {self.position}"
