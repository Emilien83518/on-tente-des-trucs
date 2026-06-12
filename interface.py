import pygame
import sys
from game import Game

# --- Constants ---
WINDOW_SIZE = 640
SQUARE_SIZE = WINDOW_SIZE // 8

# Colors
LIGHT_SQUARE  = (240, 217, 181)  # Beige — light squares
DARK_SQUARE   = (181, 136, 99)   # Brown — dark squares
HIGHLIGHT     = (186, 202, 68)   # Yellow-green — selected piece
VALID_MOVE    = (100, 200, 100)  # Green — valid move destination
WHITE_COLOR   = (255, 255, 255)
BLACK_COLOR   = (0,   0,   0)
BG_COLOR      = (30,  30,  30)   # Dark background for the menu
BTN_COLOR     = (80,  130, 80)   # Green buttons
BTN_HOVER     = (100, 160, 100)  # Lighter green when mouse is over a button
BTN_TEXT      = (255, 255, 255)  # White text on buttons
OVERLAY_COLOR = (0,   0,   0,  160)  # Semi-transparent black for the popup background


class Button:
    # Represents a clickable button on the screen

    def __init__(self, x, y, width, height, label):
        # x, y: top-left position of the button in pixels
        # width, height: size of the button
        # label: the text shown on the button
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label

    def draw(self, screen, font, mouse_pos):
        # Draws the button — changes color when the mouse is hovering over it
        # mouse_pos: current position of the mouse (x, y)
        color = BTN_HOVER if self.rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE_COLOR, self.rect, 2, border_radius=8)  # White border

        text = font.render(self.label, True, BTN_TEXT)
        # Center the text inside the button
        tx = self.rect.x + (self.rect.width  - text.get_width())  // 2
        ty = self.rect.y + (self.rect.height - text.get_height()) // 2
        screen.blit(text, (tx, ty))

    def is_clicked(self, mouse_pos):
        # Returns True if the mouse click landed inside this button
        # mouse_pos: the (x, y) position where the player clicked
        return self.rect.collidepoint(mouse_pos)


class ChessInterface:
    # Manages the entire application — the menu, the game, and the winner popup

    def __init__(self):
        # Sets up the Pygame window and all the fonts we need
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Chess Game")

        self.piece_font  = pygame.font.SysFont("segoeuisymbol", 52)  # For chess piece symbols
        self.small_font  = pygame.font.SysFont("arial", 16)          # For board coordinates
        self.button_font = pygame.font.SysFont("arial", 28, bold=True)  # For buttons
        self.title_font  = pygame.font.SysFont("arial", 60, bold=True)  # For the menu title
        self.popup_font  = pygame.font.SysFont("arial", 36, bold=True)  # For the winner message

        # The current screen the player sees: "menu" or "game"
        self.screen_state = "menu"

        self.game = None          # Created fresh each time a game starts
        self.selected_pos = None  # The square the player has clicked to select a piece
        self.valid_moves  = []    # Valid destinations for the selected piece

        # --- Menu buttons ---
        btn_w, btn_h = 220, 60
        center_x = WINDOW_SIZE // 2 - btn_w // 2
        self.btn_play  = Button(center_x, 300, btn_w, btn_h, "Play")
        self.btn_rules = Button(center_x, 390, btn_w, btn_h, "Rules")

        # --- Rules screen back button ---
        self.btn_back = Button(WINDOW_SIZE // 2 - 80, 590, 160, 44, "Back to Menu")

        # Rules scroll state — how far down the user has scrolled
        self.rules_scroll = 0

        # All the rules content — each entry is (piece_symbol, piece_name, description)
        self.rules_content = [
            ("", "Objective", "Capture the enemy King to win the game. Players alternate turns — White always goes first."),
            ("♔", "King", "Moves 1 square in any direction. The most important piece — protect it at all costs."),
            ("♕", "Queen", "Moves any number of squares in any direction: horizontally, vertically, or diagonally. The most powerful piece on the board."),
            ("♖", "Rook", "Moves any number of squares horizontally or vertically. Cannot move diagonally."),
            ("♗", "Bishop", "Moves any number of squares diagonally. Each bishop stays on the same color square for the entire game."),
            ("♘", "Knight", "Moves in an L-shape: 2 squares in one direction then 1 square sideways. The only piece that can jump over other pieces."),
            ("♙", "Pawn", "Moves 1 square forward. On its very first move, it can advance 2 squares. Captures diagonally — never straight ahead. Reaches the other end of the board to become any piece."),
        ]

        # --- Winner popup buttons ---
        popup_btn_w, popup_btn_h = 160, 50
        self.btn_rematch = Button(WINDOW_SIZE // 2 - popup_btn_w - 20, 390, popup_btn_w, popup_btn_h, "Rematch")
        self.btn_menu    = Button(WINDOW_SIZE // 2 + 20,               390, popup_btn_w, popup_btn_h, "Menu")

        # --- Promotion popup buttons (one per piece choice) ---
        promo_w, promo_h = 120, 50
        promo_y = 360
        spacing = 130
        start_x = WINDOW_SIZE // 2 - (2 * spacing) + 5
        self.btn_promo_queen  = Button(start_x,               promo_y, promo_w, promo_h, "♕ Queen")
        self.btn_promo_rook   = Button(start_x + spacing,     promo_y, promo_w, promo_h, "♖ Rook")
        self.btn_promo_bishop = Button(start_x + spacing * 2, promo_y, promo_w, promo_h, "♗ Bishop")
        self.btn_promo_knight = Button(start_x + spacing * 3, promo_y, promo_w, promo_h, "♘ Knight")

    def start_game(self):
        # Resets the game state and switches to the game screen
        self.game         = Game()
        self.selected_pos = None
        self.valid_moves  = []
        self.screen_state = "game"

    # -------------------------------------------------------------------------
    # MENU SCREEN
    # -------------------------------------------------------------------------

    def draw_menu(self):
        # Draws the main menu with the title and the two buttons
        self.screen.fill(BG_COLOR)

        # Title
        title = self.title_font.render("Chess", True, WHITE_COLOR)
        tx = WINDOW_SIZE // 2 - title.get_width() // 2
        self.screen.blit(title, (tx, 160))

        # Subtitle
        sub = self.small_font.render("A two-player chess game", True, (180, 180, 180))
        sx = WINDOW_SIZE // 2 - sub.get_width() // 2
        self.screen.blit(sub, (sx, 240))

        mouse_pos = pygame.mouse.get_pos()
        self.btn_play.draw(self.screen,  self.button_font, mouse_pos)
        self.btn_rules.draw(self.screen, self.button_font, mouse_pos)

    def handle_menu_click(self, mouse_pos):
        # Handles clicks on the main menu buttons
        # mouse_pos: where the player clicked (x, y)
        if self.btn_play.is_clicked(mouse_pos):
            self.start_game()
        elif self.btn_rules.is_clicked(mouse_pos):
            self.rules_scroll = 0          # Reset scroll to top each time we open rules
            self.screen_state = "rules"

    # -------------------------------------------------------------------------
    # RULES SCREEN
    # -------------------------------------------------------------------------

    def draw_rules(self):
        # Draws the rules screen — shows the objective and each piece's movement rules
        self.screen.fill(BG_COLOR)

        # Title
        title = self.title_font.render("Rules", True, WHITE_COLOR)
        self.screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 20))

        # Draw each rule entry, shifted up by the scroll offset
        y = 100 - self.rules_scroll
        for symbol, name, description in self.rules_content:

            if y > 570:
                break  # Don't draw below the back button

            if y > 60:  # Don't draw above the title
                # Piece symbol + name on the same line
                header = f"{symbol}  {name}" if symbol else name
                color  = (255, 220, 50) if name == "Objective" else (180, 220, 255)
                name_text = self.button_font.render(header, True, color)
                self.screen.blit(name_text, (30, y))

            y += 38

            # Description — wrap long text across multiple lines
            words = description.split()
            line, lines = "", []
            for word in words:
                test = line + (" " if line else "") + word
                if self.small_font.size(test)[0] < WINDOW_SIZE - 60:
                    line = test
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)

            for l in lines:
                if 60 < y < 570:
                    desc_text = self.small_font.render(l, True, (210, 210, 210))
                    self.screen.blit(desc_text, (40, y))
                y += 22

            y += 14  # Extra gap between each piece section

        # Divider line above back button
        pygame.draw.line(self.screen, (80, 80, 80), (20, 582), (WINDOW_SIZE - 20, 582))

        # Back button
        mouse_pos = pygame.mouse.get_pos()
        self.btn_back.draw(self.screen, self.small_font, mouse_pos)

    def handle_rules_scroll(self, direction):
        # Scrolls the rules text up or down when the player uses the mouse wheel
        # direction: -1 to scroll up, +1 to scroll down
        self.rules_scroll = max(0, self.rules_scroll + direction * 30)

    # -------------------------------------------------------------------------
    # GAME SCREEN
    # -------------------------------------------------------------------------

    def draw_board(self):
        # Draws the 8x8 chessboard with alternating colors, highlights and valid moves
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE

                if self.selected_pos == (row, col):
                    color = HIGHLIGHT

                if (row, col) in self.valid_moves:
                    color = VALID_MOVE

                pygame.draw.rect(
                    self.screen, color,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )

    def draw_coordinates(self):
        # Draws column letters (a-h) and row numbers (1-8) on the edges of the board
        columns = "abcdefgh"
        for i in range(8):
            letter = self.small_font.render(columns[i], True, BLACK_COLOR)
            self.screen.blit(letter, (i * SQUARE_SIZE + SQUARE_SIZE - 16, WINDOW_SIZE - 18))

            number = self.small_font.render(str(8 - i), True, BLACK_COLOR)
            self.screen.blit(number, (2, i * SQUARE_SIZE + 2))

    def get_piece_symbol(self, piece):
        # Returns the Unicode chess symbol for a piece (e.g. ♔ for white king)
        # piece: a piece object with a .name and .color attribute
        symbols = {
            ("King",   "white"): "♔", ("Queen",  "white"): "♕",
            ("Rook",   "white"): "♖", ("Bishop", "white"): "♗",
            ("Knight", "white"): "♘", ("Pawn",   "white"): "♙",
            ("King",   "black"): "♚", ("Queen",  "black"): "♛",
            ("Rook",   "black"): "♜", ("Bishop", "black"): "♝",
            ("Knight", "black"): "♞", ("Pawn",   "black"): "♟",
        }
        return symbols.get((piece.name, piece.color), "?")

    def draw_pieces(self):
        # Draws all pieces currently on the board using their Unicode symbols
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece is not None:
                    symbol = self.get_piece_symbol(piece)
                    text = self.piece_font.render(symbol, True, BLACK_COLOR)
                    x = col * SQUARE_SIZE + (SQUARE_SIZE - text.get_width())  // 2
                    y = row * SQUARE_SIZE + (SQUARE_SIZE - text.get_height()) // 2
                    self.screen.blit(text, (x, y))

    def draw_status_bar(self):
        # Draws the top bar showing whose turn it is, and warns if the player is in check
        if self.game.status == "Check!":
            turn_text = f"{self.game.current_turn.upper()} is in CHECK!"
            bar_color = (160, 40, 40)  # Red bar when in check
        else:
            turn_text = f"{'WHITE' if self.game.current_turn == 'white' else 'BLACK'}'s turn"
            bar_color = (40, 40, 40)
        pygame.draw.rect(self.screen, bar_color, (0, 0, WINDOW_SIZE, 24))
        label = self.small_font.render(turn_text, True, WHITE_COLOR)
        self.screen.blit(label, (10, 4))

    def get_square_from_mouse(self, mouse_x, mouse_y):
        # Converts a pixel position into a board square (row, col)
        # Returns: (row, col) tuple
        return mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE

    def handle_board_click(self, mouse_pos):
        # Handles a click on the board — selects a piece or moves it
        # mouse_pos: (x, y) pixel position of the click
        mouse_x, mouse_y = mouse_pos
        row, col = self.get_square_from_mouse(mouse_x, mouse_y)

        if self.selected_pos is None:
            piece = self.game.board.get_piece(row, col)
            if piece is not None and piece.color == self.game.current_turn:
                self.selected_pos = (row, col)
                # Use legal moves (which filter out moves that leave the king in check)
                self.valid_moves  = self.game.get_legal_moves(piece, (row, col), self.game.board.grid)
        else:
            if (row, col) in self.valid_moves:
                col_letters = "abcdefgh"
                from_row, from_col = self.selected_pos
                from_str = f"{col_letters[from_col]}{8 - from_row}"
                to_str   = f"{col_letters[col]}{8 - row}"
                self.game.play_move(f"{from_str} {to_str}")

            self.selected_pos = None
            self.valid_moves  = []

    # -------------------------------------------------------------------------
    # PROMOTION POPUP
    # -------------------------------------------------------------------------

    def draw_promotion_popup(self):
        # Draws a popup asking the player which piece they want to promote their pawn to
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Popup box
        box_w, box_h = 560, 180
        box_x = WINDOW_SIZE // 2 - box_w // 2
        box_y = WINDOW_SIZE // 2 - box_h // 2 - 10
        pygame.draw.rect(self.screen, (50, 50, 50), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(self.screen, WHITE_COLOR,  (box_x, box_y, box_w, box_h), 2, border_radius=12)

        # Title
        title = self.button_font.render("Pawn Promotion! Choose a piece:", True, (255, 220, 50))
        self.screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, box_y + 20))

        # The 4 piece buttons
        mouse_pos = pygame.mouse.get_pos()
        self.btn_promo_queen.draw(self.screen,  self.small_font, mouse_pos)
        self.btn_promo_rook.draw(self.screen,   self.small_font, mouse_pos)
        self.btn_promo_bishop.draw(self.screen, self.small_font, mouse_pos)
        self.btn_promo_knight.draw(self.screen, self.small_font, mouse_pos)

    def handle_promotion_click(self, mouse_pos):
        # Handles the player's piece choice in the promotion popup
        # mouse_pos: where the player clicked (x, y)
        row, col = self.game.pending_promotion
        if self.btn_promo_queen.is_clicked(mouse_pos):
            self.game.promote_pawn(row, col, "queen")
        elif self.btn_promo_rook.is_clicked(mouse_pos):
            self.game.promote_pawn(row, col, "rook")
        elif self.btn_promo_bishop.is_clicked(mouse_pos):
            self.game.promote_pawn(row, col, "bishop")
        elif self.btn_promo_knight.is_clicked(mouse_pos):
            self.game.promote_pawn(row, col, "knight")

    # -------------------------------------------------------------------------
    # WINNER POPUP
    # -------------------------------------------------------------------------

    def draw_winner_popup(self):
        # Draws a popup over the board announcing the winner and showing Rematch / Menu buttons

        # Semi-transparent dark overlay over the board
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Popup box
        box_w, box_h = 420, 220
        box_x = WINDOW_SIZE // 2 - box_w // 2
        box_y = WINDOW_SIZE // 2 - box_h // 2 - 20
        pygame.draw.rect(self.screen, (50, 50, 50), (box_x, box_y, box_w, box_h), border_radius=12)
        pygame.draw.rect(self.screen, WHITE_COLOR,  (box_x, box_y, box_w, box_h), 2, border_radius=12)

        # Winner message — different text for checkmate vs stalemate
        if self.game.winner:
            msg = f"{self.game.winner.upper()} WINS!"
            msg_color = (255, 220, 50)  # Gold for a winner
        else:
            msg = "STALEMATE — DRAW!"
            msg_color = (180, 180, 255)  # Blue for a draw
        winner_text = self.popup_font.render(msg, True, msg_color)
        wx = WINDOW_SIZE // 2 - winner_text.get_width() // 2
        self.screen.blit(winner_text, (wx, box_y + 30))

        # Sub-message
        sub = self.small_font.render("What would you like to do?", True, (200, 200, 200))
        sx = WINDOW_SIZE // 2 - sub.get_width() // 2
        self.screen.blit(sub, (sx, box_y + 90))

        # Rematch and Menu buttons
        mouse_pos = pygame.mouse.get_pos()
        self.btn_rematch.draw(self.screen, self.button_font, mouse_pos)
        self.btn_menu.draw(self.screen,    self.button_font, mouse_pos)

    def handle_popup_click(self, mouse_pos):
        # Handles clicks on the winner popup buttons
        # mouse_pos: where the player clicked (x, y)
        if self.btn_rematch.is_clicked(mouse_pos):
            self.start_game()  # Start a fresh game immediately
        elif self.btn_menu.is_clicked(mouse_pos):
            self.screen_state = "menu"  # Go back to the main menu

    # -------------------------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------------------------

    def run(self):
        # The main application loop — runs forever until the player closes the window
        clock = pygame.time.Clock()

        while True:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.screen_state == "menu":
                        self.handle_menu_click(mouse_pos)

                    elif self.screen_state == "rules":
                        if self.btn_back.is_clicked(mouse_pos):
                            self.screen_state = "menu"
                        # Mouse wheel buttons (4 = scroll up, 5 = scroll down)
                        elif event.button == 4:
                            self.handle_rules_scroll(-1)
                        elif event.button == 5:
                            self.handle_rules_scroll(1)

                    elif self.screen_state == "game":
                        if self.game.game_over:
                            # Game is over — clicks go to the winner popup buttons
                            self.handle_popup_click(mouse_pos)
                        elif self.game.pending_promotion:
                            # A pawn reached the last rank — player must choose a piece
                            self.handle_promotion_click(mouse_pos)
                        else:
                            # Normal play — clicks go to the board
                            self.handle_board_click(mouse_pos)

                # Mouse wheel scrolling on the rules screen
                if event.type == pygame.MOUSEWHEEL and self.screen_state == "rules":
                    self.handle_rules_scroll(-event.y)

            # Draw the correct screen depending on state
            if self.screen_state == "menu":
                self.draw_menu()

            elif self.screen_state == "rules":
                self.draw_rules()

            elif self.screen_state == "game":
                self.draw_board()
                self.draw_pieces()
                self.draw_coordinates()
                self.draw_status_bar()

                if self.game.pending_promotion:
                    self.draw_promotion_popup()
                elif self.game.game_over:
                    self.draw_winner_popup()

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    # Launch the application starting from the main menu
    ChessInterface().run()
