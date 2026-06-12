"""
Permanent test suite for the chess game.
Run with: python -m pytest tests/ -v
Or:        python tests/test_game.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import Game
from pieces.king import King
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.pawn import Pawn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def empty_grid():
    # Returns a blank 8x8 board with no pieces on it
    return [[None] * 8 for _ in range(8)]

def make_game_with_grid(grid):
    # Creates a Game whose board uses the given custom grid
    # grid: an 8x8 list of pieces / None values
    g = Game()
    g.board.grid = grid
    return g


# ---------------------------------------------------------------------------
# Basic game setup
# ---------------------------------------------------------------------------

def test_game_starts_white():
    assert Game().current_turn == "white"

def test_game_starts_not_over():
    assert Game().game_over == False

def test_board_created():
    assert Game().board is not None


# ---------------------------------------------------------------------------
# Move parsing
# ---------------------------------------------------------------------------

def test_parse_move_valid():
    g = Game()
    result = g.parse_move("e2 e4")
    assert result == ((6, 4), (4, 4))

def test_parse_move_invalid_string():
    assert Game().parse_move("bad input") is None

def test_parse_move_single_word():
    assert Game().parse_move("e2") is None


# ---------------------------------------------------------------------------
# Turn management
# ---------------------------------------------------------------------------

def test_switch_turn():
    g = Game()
    g.switch_turn()
    assert g.current_turn == "black"
    g.switch_turn()
    assert g.current_turn == "white"

def test_cannot_move_wrong_color():
    g = Game()
    g.play_move("e2 e4")  # white moves
    result = g.play_move("d2 d4")  # white tries again
    assert "black" in result.lower() and "turn" in result.lower()


# ---------------------------------------------------------------------------
# Check detection
# ---------------------------------------------------------------------------

def test_king_in_check_from_rook():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[0][4] = Rook("black", (0, 4))
    assert g.is_in_check("white", grid)

def test_king_not_in_check():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    assert not g.is_in_check("white", grid)

def test_king_cannot_move_into_check():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[5][5] = Rook("black", (5, 5))
    king = grid[7][4]
    legal = g.get_legal_moves(king, (7, 4), grid)
    assert (7, 5) not in legal  # col 5 attacked by rook

def test_pinned_piece_cannot_expose_king():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[7][3] = Rook("white", (7, 3))  # Shields king
    grid[7][0] = Rook("black", (7, 0))  # Attacks along row 7
    rook = grid[7][3]
    legal = g.get_legal_moves(rook, (7, 3), grid)
    assert all(r == 7 for r, c in legal)  # Can only move along row 7

def test_play_move_rejects_exposing_king():
    g = make_game_with_grid(empty_grid())
    g.board.grid[7][4] = King("white", (7, 4))
    g.board.grid[7][3] = Rook("white", (7, 3))
    g.board.grid[7][0] = Rook("black", (7, 0))
    g.board.grid[0][0] = King("black", (0, 0))
    result = g.play_move("d1 d5")
    assert "check" in result.lower()


# ---------------------------------------------------------------------------
# Checkmate and stalemate
# ---------------------------------------------------------------------------

def test_checkmate_detected():
    g = Game()
    grid = empty_grid()
    grid[0][0] = King("black",  (0, 0))
    grid[1][1] = Queen("white", (1, 1))
    grid[0][2] = Rook("white",  (0, 2))
    grid[7][1] = Rook("white",  (7, 1))
    assert g.is_in_check("black", grid)
    assert not g.has_any_legal_move("black", grid)

def test_stalemate_detected():
    g = Game()
    grid = empty_grid()
    grid[0][7] = King("black",  (0, 7))
    grid[2][6] = Queen("white", (2, 6))
    grid[7][0] = King("white",  (7, 0))
    assert not g.is_in_check("black", grid)
    assert not g.has_any_legal_move("black", grid)


# ---------------------------------------------------------------------------
# Castling
# ---------------------------------------------------------------------------

def test_kingside_castling_available():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[7][7] = Rook("white", (7, 7))
    king = grid[7][4]
    assert (7, 6) in g.get_legal_moves(king, (7, 4), grid)

def test_queenside_castling_available():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[7][0] = Rook("white", (7, 0))
    king = grid[7][4]
    assert (7, 2) in g.get_legal_moves(king, (7, 4), grid)

def test_castling_blocked_by_piece():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[7][7] = Rook("white", (7, 7))
    grid[7][6] = Rook("white", (7, 6))  # Blocks path
    king = grid[7][4]
    assert (7, 6) not in g.get_legal_moves(king, (7, 4), grid)

def test_castling_blocked_through_check():
    g = Game()
    grid = empty_grid()
    grid[7][4] = King("white", (7, 4))
    grid[7][7] = Rook("white", (7, 7))
    grid[0][5] = Rook("black", (0, 5))  # Attacks f1 — king passes through
    grid[0][4] = King("black", (0, 4))
    king = grid[7][4]
    assert (7, 6) not in g.get_legal_moves(king, (7, 4), grid)

def test_rook_moves_after_castling():
    g = Game()
    g.board.grid[7][5] = None
    g.board.grid[7][6] = None
    g.play_move("e1 g1")
    assert g.board.grid[7][5] is not None
    assert g.board.grid[7][5].name == "Rook"
    assert g.board.grid[7][7] is None


# ---------------------------------------------------------------------------
# Pawn promotion
# ---------------------------------------------------------------------------

def test_promotion_triggered():
    g = make_game_with_grid(empty_grid())
    g.board.grid[1][0] = Pawn("white", (1, 0))
    g.board.grid[7][4] = King("white", (7, 4))
    g.board.grid[0][4] = King("black", (0, 4))
    g.play_move("a7 a8")
    assert g.pending_promotion == (0, 0)

def test_promotion_to_queen():
    g = make_game_with_grid(empty_grid())
    g.board.grid[1][0] = Pawn("white", (1, 0))
    g.board.grid[7][4] = King("white", (7, 4))
    g.board.grid[0][4] = King("black", (0, 4))
    g.play_move("a7 a8")
    g.promote_pawn(0, 0, "queen")
    assert g.board.grid[0][0].name == "Queen"

def test_promotion_to_knight():
    g = make_game_with_grid(empty_grid())
    g.board.grid[1][3] = Pawn("white", (1, 3))
    g.board.grid[7][4] = King("white", (7, 4))
    g.board.grid[0][4] = King("black", (0, 4))
    g.play_move("d7 d8")
    g.promote_pawn(0, 3, "knight")
    assert g.board.grid[0][3].name == "Knight"


# ---------------------------------------------------------------------------
# En passant
# ---------------------------------------------------------------------------

def test_en_passant_target_set_after_double_step():
    g = Game()
    g.play_move("e2 e4")  # White pawn double step
    assert g.en_passant_target == (5, 4)  # The square e3 that was skipped

def test_en_passant_target_cleared_after_other_move():
    g = Game()
    g.play_move("e2 e4")  # White double step — sets en passant
    g.play_move("a7 a6")  # Black plays something else — clears it
    assert g.en_passant_target is None

def test_en_passant_capture_removes_pawn():
    # White pawn at e4 (row 4, col 4) just double-stepped from e2, skipping e3 (row 5, col 4)
    # Black pawn at d4 (row 4, col 3) captures en passant to e3 (row 5, col 4)
    g = make_game_with_grid(empty_grid())
    g.board.grid[4][4] = Pawn("white", (4, 4))  # White pawn at e4
    g.board.grid[4][3] = Pawn("black", (4, 3))  # Black pawn at d4
    g.board.grid[7][0] = King("white", (7, 0))
    g.board.grid[0][0] = King("black", (0, 0))
    g.current_turn = "black"
    g.en_passant_target = (5, 4)  # e3 — the square white's pawn skipped over
    g.play_move("d4 e3")          # Black captures en passant
    assert g.board.grid[4][4] is None   # Captured white pawn is gone
    assert g.board.grid[5][4] is not None  # Black pawn is now at e3

def test_en_passant_only_available_one_turn():
    g = Game()
    g.play_move("e2 e4")  # Sets en passant target at e3
    g.play_move("d7 d5")  # Black plays — clears white's en passant
    g.play_move("d2 d4")  # White plays another double step
    g.play_move("a7 a6")  # Black plays something else — clears en passant
    assert g.en_passant_target is None


# ---------------------------------------------------------------------------
# 50-move rule
# ---------------------------------------------------------------------------

def test_halfmove_clock_increments():
    g = Game()
    g.play_move("g1 f3")  # Knight move — not a pawn move, not a capture
    assert g.halfmove_clock == 1

def test_halfmove_clock_resets_on_pawn_move():
    g = Game()
    g.play_move("g1 f3")  # Increments clock
    g.play_move("e7 e5")  # Pawn move — resets clock
    assert g.halfmove_clock == 0

def test_50_move_draw():
    g = Game()
    g.halfmove_clock = 100  # Simulate 50 full moves without pawn or capture
    g._check_game_state()
    assert g.game_over
    assert g.winner is None
    assert "50" in g.status


# ---------------------------------------------------------------------------
# Threefold repetition
# ---------------------------------------------------------------------------

def test_threefold_repetition_draw():
    g = Game()
    snapshot = g._board_snapshot()
    g.position_history = [snapshot, snapshot, snapshot]  # Same position 3 times
    g._check_game_state()
    assert g.game_over
    assert g.winner is None
    assert "repetition" in g.status.lower()


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback
    passed = failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  PASS - {name}")
                passed += 1
            except Exception as e:
                print(f"  FAIL - {name}: {e}")
                traceback.print_exc()
                failed += 1
    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*40}")
    sys.exit(0 if failed == 0 else 1)
