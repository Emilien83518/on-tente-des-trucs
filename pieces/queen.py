class Queen:
    # Represents the Queen piece in a chess game
    # The queen is the most powerful piece — she can move in any direction and any number of squares

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the queen is on the board (e.g. (0, 3))
        self.color = color
        self.position = position
        self.name = "Queen"

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the queen can move to from her current position
        # The queen combines the moves of a rook (straight lines) and a bishop (diagonals)
        moves = []

        # All 8 directions the queen can move:
        # (row_step, col_step)
        directions = [
            (-1,  0),  # up
            ( 1,  0),  # down
            ( 0, -1),  # left
            ( 0,  1),  # right
            (-1, -1),  # up-left diagonal
            (-1,  1),  # up-right diagonal
            ( 1, -1),  # down-left diagonal
            ( 1,  1),  # down-right diagonal
        ]

        row, col = self.position

        for row_step, col_step in directions:
            # For each direction, keep moving until we hit the edge of the board or another piece
            current_row = row + row_step
            current_col = col + col_step

            while self._is_on_board(current_row, current_col):
                target = board[current_row][current_col]

                if target is None:
                    # Empty square — the queen can move here
                    moves.append((current_row, current_col))
                elif target.color != self.color:
                    # Enemy piece — the queen can capture it, but cannot go further
                    moves.append((current_row, current_col))
                    break
                else:
                    # Friendly piece — the queen is blocked, cannot move here or further
                    break

                current_row += row_step
                current_col += col_step

        return moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        # Returns True if valid, False if out of bounds
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the queen to a new position on the board
        # new_position: a tuple (row, col) of the destination square
        self.position = new_position

    def __repr__(self):
        # Returns a readable string describing the queen — useful for debugging
        return f"{self.color.capitalize()} Queen at {self.position}"
