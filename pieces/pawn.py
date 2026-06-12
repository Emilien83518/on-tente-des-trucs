class Pawn:
    # Represents the Pawn piece in a chess game
    # The pawn is the most numerous piece — each player starts with 8
    # Pawns move forward but capture diagonally, and have special rules like the first-move double step

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the pawn is on the board
        # White pawns move "up" (decreasing row), black pawns move "down" (increasing row)
        self.color = color
        self.position = position
        self.name = "Pawn"
        self.has_moved = False  # Tracks if the pawn has already moved (needed for the double step rule)

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the pawn can move to
        moves = []

        row, col = self.position

        # White moves up (row decreases), black moves down (row increases)
        direction = -1 if self.color == "white" else 1

        # --- Forward move (1 square) ---
        one_step = row + direction
        if self._is_on_board(one_step, col) and board[one_step][col] is None:
            # The square directly in front must be empty — pawns cannot capture forward
            moves.append((one_step, col))

            # --- Double step on first move ---
            two_step = row + 2 * direction
            if not self.has_moved and self._is_on_board(two_step, col) and board[two_step][col] is None:
                # The pawn can move 2 squares forward only if it hasn't moved yet
                # and both squares in front are empty
                moves.append((two_step, col))

        # --- Diagonal captures ---
        for col_offset in [-1, 1]:
            capture_row = row + direction
            capture_col = col + col_offset

            if self._is_on_board(capture_row, capture_col):
                target = board[capture_row][capture_col]
                if target is not None and target.color != self.color:
                    # There is an enemy piece on the diagonal — the pawn can capture it
                    moves.append((capture_row, capture_col))

        return moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the pawn to a new position and marks that it has moved
        self.position = new_position
        self.has_moved = True

    def is_promotion(self):
        # Checks if the pawn has reached the opposite end of the board
        # White pawns promote at row 0, black pawns promote at row 7
        row, col = self.position
        if self.color == "white" and row == 0:
            return True
        if self.color == "black" and row == 7:
            return True
        return False

    def __repr__(self):
        # Returns a readable string describing the pawn — useful for debugging
        return f"{self.color.capitalize()} Pawn at {self.position}"
