class Rook:
    # Represents the Rook piece in a chess game
    # The rook moves in straight lines — horizontally or vertically — any number of squares

    def __init__(self, color, position):
        # color: "white" or "black"
        # position: a tuple (row, col) representing where the rook is on the board
        self.color = color
        self.position = position
        self.name = "Rook"
        self.has_moved = False  # Tracks if the rook has moved (needed for castling)

    def get_valid_moves(self, board):
        # Returns a list of all valid positions the rook can move to
        # The rook moves in 4 straight directions and can go as far as possible
        moves = []

        # The 4 straight directions the rook can move
        directions = [
            (-1,  0),  # up
            ( 1,  0),  # down
            ( 0, -1),  # left
            ( 0,  1),  # right
        ]

        row, col = self.position

        for row_step, col_step in directions:
            current_row = row + row_step
            current_col = col + col_step

            while self._is_on_board(current_row, current_col):
                target = board[current_row][current_col]

                if target is None:
                    # Empty square — the rook can move here
                    moves.append((current_row, current_col))
                elif target.color != self.color:
                    # Enemy piece — the rook can capture it, but cannot go further
                    moves.append((current_row, current_col))
                    break
                else:
                    # Friendly piece — the rook is blocked
                    break

                current_row += row_step
                current_col += col_step

        return moves

    def _is_on_board(self, row, col):
        # Checks if a position is within the 8x8 chess board
        return 0 <= row <= 7 and 0 <= col <= 7

    def move(self, new_position):
        # Moves the rook to a new position and marks that he has moved
        self.position = new_position
        self.has_moved = True

    def __repr__(self):
        # Returns a readable string describing the rook — useful for debugging
        return f"{self.color.capitalize()} Rook at {self.position}"
