class Bishop:
    # Represents the Bishop piece in a chess game
    # The bishop moves diagonally any number of squares
    # Each bishop stays on the same color of square for the entire game

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the bishop is on the board
        self.color = color
        self.position = position
        self.name = "Bishop"

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the bishop can move to
        # The bishop moves in 4 diagonal directions and can go as far as possible
        moves = []

        # The 4 diagonal directions the bishop can move
        directions = [
            (-1, -1),  # up-left
            (-1,  1),  # up-right
            ( 1, -1),  # down-left
            ( 1,  1),  # down-right
        ]

        row, col = self.position

        for row_step, col_step in directions:
            current_row = row + row_step
            current_col = col + col_step

            while self._is_on_board(current_row, current_col):
                target = board[current_row][current_col]

                if target is None:
                    # Empty square — the bishop can move here
                    moves.append((current_row, current_col))
                elif target.color != self.color:
                    # Enemy piece — the bishop can capture it, but cannot go further
                    moves.append((current_row, current_col))
                    break
                else:
                    # Friendly piece — the bishop is blocked
                    break

                current_row += row_step
                current_col += col_step

        return moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the bishop to a new position
        self.position = new_position

    def __repr__(self):
        # Returns a readable string describing the bishop — useful for debugging
        return f"{self.color.capitalize()} Bishop at {self.position}"
