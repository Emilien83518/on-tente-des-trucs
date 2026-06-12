class King:
    # Represents the King piece in a chess game
    # The king is the most important piece — if he is captured, the game is over
    # He can move exactly 1 square in any direction

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the king is on the board
        self.color = color
        self.position = position
        self.name = "King"
        self.has_moved = False  # Tracks if the king has moved (needed for castling)

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the king can move to
        # The king moves exactly 1 square in any of the 8 directions
        moves = []

        # All 8 directions the king can move (1 square each)
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
            new_row = row + row_step
            new_col = col + col_step

            if self._is_on_board(new_row, new_col):
                target = board[new_row][new_col]

                if target is None:
                    # Empty square — the king can move here
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    # Enemy piece — the king can capture it
                    moves.append((new_row, new_col))
                # If friendly piece, the king cannot move there

        return moves

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
