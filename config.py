#!/usr/bin/env python3
"""
Configuration file for ChessPredictor with enhanced board display
"""

import os

# Paths
PIECES_PATH = "pieces"

# Colors (updated for better appearance)
COLORS = ['w', 'b']  # White, Black
PIECE_TYPES = ['P', 'R', 'N', 'B', 'Q', 'K']  # Pawn, Rook, Knight, Bishop, Queen, King

# Window and board dimensions (with space for labels)
WINDOW_WIDTH = 1100   # 680 for board + labels + 320 for controls
WINDOW_HEIGHT = 720   # 680 for board + labels + some padding
BOARD_SIZE = 640      # Main board area
SQUARE_SIZE = BOARD_SIZE // 8  # 80px per square

# Board positioning (leave space for labels)
BOARD_OFFSET_X = 40   # Space for rank labels (1-8)
BOARD_OFFSET_Y = 40   # Space for file labels (a-h)

# Control panel positioning (adjusted for labels)
CONTROL_PANEL_X = BOARD_SIZE + BOARD_OFFSET_X + 20
CONTROL_PANEL_WIDTH = WINDOW_WIDTH - CONTROL_PANEL_X - 10

# Piece sizing - optimized for better centering
PIECE_SCALE = 0.8     # Smaller pieces for better fit
PIECE_SIZE = int(SQUARE_SIZE * PIECE_SCALE)
PIECE_OFFSET = (SQUARE_SIZE - PIECE_SIZE) // 2  # For centering (now unused but kept for compatibility)

# Colors
LIGHT_SQUARE = (240, 217, 181)    # Light brown
DARK_SQUARE = (181, 136, 99)      # Dark brown
BOARD_BORDER = (101, 67, 33)      # Dark border
LABEL_COLOR = (60, 40, 20)        # Dark text for labels
PANEL_BACKGROUND = (245, 245, 245)
TEXT_COLOR = (50, 50, 50)
BUTTON_COLOR = (200, 200, 200)
BUTTON_ACTIVE = (150, 200, 150)
VALID_MOVE_DOT = (100, 150, 100, 180)

# Game modes
SETUP_MODE = "setup"
ANALYSIS_MODE = "analysis"
PLAY_MODE = "play"

def get_piece_path(piece_name, use_svg=False):
    """Get path to piece image file"""
    ext = 'svg' if use_svg else 'png'
    return os.path.join(PIECES_PATH, ext, f"{piece_name}.{ext}")

def validate_piece_files(use_svg=False):
    """Validate that all piece files exist"""
    for color in COLORS:
        for piece in PIECE_TYPES:
            path = get_piece_path(f"{color}{piece}", use_svg)
            if not os.path.exists(path):
                print(f"Missing piece file: {path}")
                return False
    return True