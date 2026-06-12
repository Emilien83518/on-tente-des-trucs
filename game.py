from board import Board


class Game:
    # Manages the overall chess game — tracks whose turn it is and whether the game is over

    def __init__(self):
        # Sets up a fresh game with a new board and gives the first turn to white
        self.board = Board()
        self.current_turn = "white"  # White always goes first in chess
        self.game_over = False
        self.winner = None

    def switch_turn(self):
        # Switches the turn from white to black, or from black to white
        if self.current_turn == "white":
            self.current_turn = "black"
        else:
            self.current_turn = "white"

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
            from_row = 8 - int(parts[0][1])  # Chess rows go 8 (top) to 1 (bottom)
            to_col = col_map.get(parts[1][0])
            to_row = 8 - int(parts[1][1])

            if None in (from_col, to_col):
                return None

            return (from_row, from_col), (to_row, to_col)
        except (IndexError, ValueError):
            return None

    def play_move(self, move_str):
        # Tries to apply a move given as a string like "e2 e4"
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

        success = self.board.move_piece(from_pos, to_pos)

        if not success:
            return "Invalid move for that piece."

        # Check if the enemy king has been captured (simplified win condition)
        if self._is_king_captured():
            self.game_over = True
            self.winner = self.current_turn
            return f"GAME OVER — {self.current_turn} wins!"

        self.switch_turn()
        return f"Move accepted. It is now {self.current_turn}'s turn."

    def _is_king_captured(self):
        # Checks if either king is missing from the board — if so, the game is over
        # Returns True if a king has been captured
        kings_found = {"white": False, "black": False}

        for row in self.board.grid:
            for piece in row:
                if piece is not None and piece.name == "King":
                    kings_found[piece.color] = True

        # If either king is not found, someone has won
        return not kings_found["white"] or not kings_found["black"]

    def get_board_display(self):
        # Returns the board as a string so it can be sent over the network and printed in the terminal
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        self.board.display()
        sys.stdout = old_stdout
        return buffer.getvalue()
