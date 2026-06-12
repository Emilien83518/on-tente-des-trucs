class Knight:
    # Represents the Knight piece in a chess game
    # The knight moves in an "L" shape: 2 squares in one direction, then 1 square perpendicular
    # The knight is the only piece that can jump over other pieces

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the knight is on the board
        self.color = color
        self.position = position
        self.name = "Knight"

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the knight can move to
        # The knight always moves in an L-shape — 8 possible landing spots maximum
        moves = []

        # All 8 possible L-shape moves for the knight
        l_shapes = [
            (-2, -1),  # 2 up, 1 left
            (-2,  1),  # 2 up, 1 right
            ( 2, -1),  # 2 down, 1 left
            ( 2,  1),  # 2 down, 1 right
            (-1, -2),  # 1 up, 2 left
            (-1,  2),  # 1 up, 2 right
            ( 1, -2),  # 1 down, 2 left
            ( 1,  2),  # 1 down, 2 right
        ]

        row, col = self.position

        for row_step, col_step in l_shapes:
            new_row = row + row_step
            new_col = col + col_step

            if self._is_on_board(new_row, new_col):
                target = board[new_row][new_col]

                if target is None:
                    # Empty square — the knight can land here
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    # Enemy piece — the knight can capture it
                    moves.append((new_row, new_col))
                # If friendly piece, the knight cannot land there

        return moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the knight to a new position
        self.position = new_position

    def __repr__(self):
        # Returns a readable string describing the knight — useful for debugging
        return f"{self.color.capitalize()} Knight at {self.position}"
