import chess
import pygame
import pygame.gfxdraw
import threading
import time
from typing import Optional, Dict, List, Tuple
from config import *
try:
    from stockfish import Stockfish
    STOCKFISH_AVAILABLE = True
except ImportError:
    STOCKFISH_AVAILABLE = False
    print("Warning: stockfish library not installed. Run: pip install stockfish")
from eval import evaluate_board

class ChessPredictor:
    def __init__(self, use_svg=True, stockfish_path=None):
        print("Starting ChessPredictor initialization...")
        
        try:
            print("1. Initializing Pygame...")
            pygame.init()
            pygame.font.init()
            print("✓ Pygame initialized")
            
            print("2. Creating display...")
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("ChessPredictor-Proto v1.0")
            print("✓ Display created")
            
            print("3. Initializing fonts...")
            # Initialize fonts
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)
            print("✓ Fonts initialized")
            
            print("4. Validating piece files...")
            # Validate and load pieces
            if not validate_piece_files(use_svg):
                print("✗ Piece file validation failed")
                pygame.quit()
                exit(1)
            print("✓ Piece files validated")
                
            print("5. Loading piece sprites...")
            self.pieces = {}
            self.load_pieces(use_svg)
            print("✓ Piece sprites loaded")
            
            print("6. Initializing game state...")
            # Initialize game state
            self.board = chess.Board()
            self.selected_piece = None
            self.dragging = False
            self.valid_moves = set()
            print("✓ Game state initialized")
            
            print("7. Setting up game modes...")
            # Game modes and settings
            self.current_mode = SETUP_MODE
            self.active_color = chess.WHITE  # Who to move
            self.castling_rights = {
                'white_kingside': True,
                'white_queenside': True,
                'black_kingside': True,
                'black_queenside': True
            }
            self.play_vs_ai = False
            print("✓ Game modes configured")
            
            print("8. Initializing AI variables...")
            # AI and analysis
            self.stockfish_ai = None
            self.ai_thinking = False
            self.last_ai_move = None
            self.last_ai_eval = None
            self.stockfish_comparison = None
            self.ai_suggested_square = None  # For highlighting AI suggestion
            print("✓ AI variables initialized")
            
            print("9. Creating UI elements...")
            # UI state
            self.buttons = {}
            self.create_ui_elements()
            print("✓ UI elements created")
                
            print("10. Initializing game history...")
            # Game history
            self.move_history = []
            self.position_history = []
            print("✓ Game history initialized")
                
            print("11. Initializing Stockfish (this may take a moment)...")
            # Initialize Stockfish using library approach (no direct .exe calls)
            try:
                print("   - Checking if stockfish library is available...")
                if not STOCKFISH_AVAILABLE:
                    print("   - ✗ stockfish library not installed")
                    print("   - Run: pip install stockfish")
                    self.stockfish_ai = None
                else:
                    print("   - ✓ stockfish library available")
                    
                    print("   - Creating Stockfish instance using library...")
                    # The library handles the exe internally - we just pass the path
                    self.stockfish_ai = Stockfish(path=stockfish_path or "stockfish.exe")
                    print("   - ✓ Stockfish instance created")
                    
                    print("   - Setting parameters...")
                    self.stockfish_ai.set_depth(10)
                    self.stockfish_ai.set_skill_level(15)
                    print("   - ✓ Parameters set")
                    
                    print("   - Testing basic functionality...")
                    test_board = chess.Board()
                    self.stockfish_ai.set_fen_position(test_board.fen())
                    
                    evaluation = self.stockfish_ai.get_evaluation()
                    print(f"   - ✓ Evaluation: {evaluation}")
                    
                    top_moves = self.stockfish_ai.get_top_moves(3)
                    if top_moves:
                        print(f"   - ✓ Top move: {top_moves[0]['Move']}")
                        print("   - ✅ Stockfish working!")
                    else:
                        print("   - ⚠️  No moves returned")
                        
            except Exception as e:
                print(f"   - ✗ Stockfish failed: {e}")
                self.stockfish_ai = None
            
            print("✓ Stockfish initialization completed")
            print("✅ ChessPredictor initialization successful!")
                
        except Exception as e:
            print(f"❌ Initialization failed at step: {e}")
            import traceback
            traceback.print_exc()
            if 'pygame' in locals():
                pygame.quit()
            exit(1)
    
    def load_pieces(self, use_svg):
        """Load piece sprites"""
        for color in COLORS:
            for piece in PIECE_TYPES:
                try:
                    path = get_piece_path(f"{color}{piece}", use_svg)
                    img = pygame.image.load(path)
                    self.pieces[f"{color}{piece}"] = pygame.transform.smoothscale(
                        img, (PIECE_SIZE, PIECE_SIZE)
                    )
                except pygame.error as e:
                    print(f"Error loading piece {color}{piece}: {e}")
                    pygame.quit()
                    exit(1)
    
    def create_ui_elements(self):
        """Create UI buttons and controls"""
        self.buttons = {
            # Mode selection - make them more visible
            'setup_mode': pygame.Rect(CONTROL_PANEL_X + 10, 40, 80, 25),
            'analysis_mode': pygame.Rect(CONTROL_PANEL_X + 95, 40, 80, 25),
            'play_mode': pygame.Rect(CONTROL_PANEL_X + 180, 40, 80, 25),
            
            # Active color
            'white_to_move': pygame.Rect(CONTROL_PANEL_X + 27, 100, 15, 15),
            'black_to_move': pygame.Rect(CONTROL_PANEL_X + 27, 125, 15, 15),
            
            # Castling rights
            'white_kingside': pygame.Rect(CONTROL_PANEL_X + 20, 170, 15, 15),
            'white_queenside': pygame.Rect(CONTROL_PANEL_X + 20, 190, 15, 15),
            'black_kingside': pygame.Rect(CONTROL_PANEL_X + 20, 210, 15, 15),
            'black_queenside': pygame.Rect(CONTROL_PANEL_X + 20, 230, 15, 15),
            
            # Actions
            'clear_board': pygame.Rect(CONTROL_PANEL_X + 10, 270, 100, 25),
            'reset_position': pygame.Rect(CONTROL_PANEL_X + 120, 270, 100, 25),
            'get_best_move': pygame.Rect(CONTROL_PANEL_X + 230, 270, 100, 25),
            'toggle_vs_ai': pygame.Rect(CONTROL_PANEL_X + 10, 300, 100, 25),
        }
    
    def draw_board(self):
        """Draw the chess board with file/rank labels"""
        # Draw file labels (a-h) at bottom
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, file_label in enumerate(files):
            x = BOARD_OFFSET_X + i * SQUARE_SIZE + SQUARE_SIZE // 2
            y = BOARD_OFFSET_Y + BOARD_SIZE + 10
            label = self.font_medium.render(file_label, True, LABEL_COLOR)
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)
        
        # Draw rank labels (1-8) on left side
        ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        for i, rank_label in enumerate(ranks):
            x = BOARD_OFFSET_X - 20
            y = BOARD_OFFSET_Y + (7 - i) * SQUARE_SIZE + SQUARE_SIZE // 2
            label = self.font_medium.render(rank_label, True, LABEL_COLOR)
            label_rect = label.get_rect(center=(x, y))
            self.screen.blit(label, label_rect)
        
        # Draw board border
        border_rect = pygame.Rect(BOARD_OFFSET_X - 2, BOARD_OFFSET_Y - 2, 
                                BOARD_SIZE + 4, BOARD_SIZE + 4)
        pygame.draw.rect(self.screen, BOARD_BORDER, border_rect, 3)
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                
                # Highlight selected piece
                if self.selected_piece == square:
                    color = (255, 255, 0, 100)  # Yellow highlight for selected piece
                
                # Highlight AI suggested move
                if self.ai_suggested_square == square:
                    color = (0, 255, 0, 100)  # Green highlight for AI suggestion
                
                x = BOARD_OFFSET_X + col * SQUARE_SIZE
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                pygame.draw.rect(self.screen, color, 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw valid move dots (larger and more visible)
        if self.selected_piece and self.current_mode != SETUP_MODE:
            for move in self.valid_moves:
                center_x = BOARD_OFFSET_X + (chess.square_file(move) * SQUARE_SIZE) + SQUARE_SIZE // 2
                center_y = BOARD_OFFSET_Y + (7 - chess.square_rank(move)) * SQUARE_SIZE + SQUARE_SIZE // 2
                # Draw larger, more visible dots for legal moves
                pygame.gfxdraw.filled_circle(
                    self.screen, center_x, center_y, 
                    SQUARE_SIZE // 6, (0, 255, 0, 150)  # Larger green dots
                )
                pygame.gfxdraw.aacircle(
                    self.screen, center_x, center_y, 
                    SQUARE_SIZE // 6, (0, 200, 0)  # Green border
                )
    
    def draw_pieces(self):
        """Draw chess pieces properly centered in squares"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'w' if piece.color else 'b'
                piece_key = f"{color}{piece.symbol().upper()}"
                
                # Calculate center position of the square
                square_center_x = BOARD_OFFSET_X + chess.square_file(square) * SQUARE_SIZE + SQUARE_SIZE // 2
                square_center_y = BOARD_OFFSET_Y + (7 - chess.square_rank(square)) * SQUARE_SIZE + SQUARE_SIZE // 2
                
                # Position piece centered in the square
                piece_x = square_center_x - PIECE_SIZE // 2 + PIECE_OFFSET + 10
                piece_y = square_center_y - PIECE_SIZE // 2 + PIECE_OFFSET + 10

                # Don't draw the piece being dragged
                if self.dragging and self.selected_piece == square:
                    continue
                    
                self.screen.blit(self.pieces[piece_key], (piece_x, piece_y))
    
    def draw_control_panel(self):
        """Draw the control panel"""
        # Background
        pygame.draw.rect(self.screen, PANEL_BACKGROUND, 
                        (CONTROL_PANEL_X, 0, CONTROL_PANEL_WIDTH, WINDOW_HEIGHT))
        
        # Title
        title = self.font_large.render("ChessPredictor v1.0", True, TEXT_COLOR)
        self.screen.blit(title, (CONTROL_PANEL_X + 10, 10))
        
        # Mode selection with clear borders
        y_offset = 40
        mode_text = self.font_small.render("Mode:", True, TEXT_COLOR)
        self.screen.blit(mode_text, (CONTROL_PANEL_X + 10, y_offset - 15))
        
        modes = [SETUP_MODE, ANALYSIS_MODE, PLAY_MODE]
        mode_labels = ["Setup", "Analysis", "Play"]
        
        for i, (mode, label) in enumerate(zip(modes, mode_labels)):
            btn_rect = self.buttons[f'{mode}_mode']
            color = BUTTON_ACTIVE if self.current_mode == mode else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, btn_rect, 2)
            
            text = self.font_small.render(label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
        
        # Current mode indicator
        mode_indicator = self.font_small.render(f"Current: {self.current_mode.title()}", True, (0, 100, 0))
        self.screen.blit(mode_indicator, (CONTROL_PANEL_X + 10, y_offset + 30))
        
        # Active color
        y_offset = 100
        color_text = self.font_small.render("Active Color:", True, TEXT_COLOR)
        self.screen.blit(color_text, (CONTROL_PANEL_X + 10, y_offset - 15))
        
        # White to move radio button
        pygame.draw.circle(self.screen, (255, 255, 255), 
                         (CONTROL_PANEL_X + 34, y_offset + 7), 8)
        pygame.draw.circle(self.screen, TEXT_COLOR, 
                         (CONTROL_PANEL_X + 34, y_offset + 7), 8, 2)
        if self.active_color == chess.WHITE:
            pygame.draw.circle(self.screen, TEXT_COLOR, 
                             (CONTROL_PANEL_X + 34, y_offset + 7), 4)
        
        white_text = self.font_small.render("White to move", True, TEXT_COLOR)
        self.screen.blit(white_text, (CONTROL_PANEL_X + 50, y_offset))
        
        # Black to move radio button
        pygame.draw.circle(self.screen, (255, 255, 255), 
                         (CONTROL_PANEL_X + 34, y_offset + 32), 8)
        pygame.draw.circle(self.screen, TEXT_COLOR, 
                         (CONTROL_PANEL_X + 34, y_offset + 32), 8, 2)
        if self.active_color == chess.BLACK:
            pygame.draw.circle(self.screen, TEXT_COLOR, 
                             (CONTROL_PANEL_X + 34, y_offset + 32), 4)
        
        black_text = self.font_small.render("Black to move", True, TEXT_COLOR)
        self.screen.blit(black_text, (CONTROL_PANEL_X + 50, y_offset + 25))
        
        # Castling availability
        y_offset = 170
        castling_text = self.font_small.render("Castling Rights:", True, TEXT_COLOR)
        self.screen.blit(castling_text, (CONTROL_PANEL_X + 10, y_offset - 15))
        
        castling_options = [
            ('white_kingside', 'White kingside', 170),
            ('white_queenside', 'White queenside', 190),
            ('black_kingside', 'Black kingside', 210),
            ('black_queenside', 'Black queenside', 230)
        ]
        
        for key, label, y_pos in castling_options:
            # Checkbox
            checkbox_rect = pygame.Rect(CONTROL_PANEL_X + 20, y_pos, 15, 15)
            pygame.draw.rect(self.screen, (255, 255, 255), checkbox_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, checkbox_rect, 2)
            
            if self.castling_rights[key]:
                pygame.draw.line(self.screen, TEXT_COLOR,
                               (CONTROL_PANEL_X + 23, y_pos + 7),
                               (CONTROL_PANEL_X + 27, y_pos + 11), 2)
                pygame.draw.line(self.screen, TEXT_COLOR,
                               (CONTROL_PANEL_X + 27, y_pos + 11),
                               (CONTROL_PANEL_X + 32, y_pos + 4), 2)
            
            text = self.font_small.render(label, True, TEXT_COLOR)
            self.screen.blit(text, (CONTROL_PANEL_X + 40, y_pos))
        
        # Action buttons with better spacing
        y_offset = 270
        buttons_info = [
            ('clear_board', 'Clear Board'),
            ('reset_position', 'Reset'),
            ('get_best_move', 'Best Move'),
            ('toggle_vs_ai', 'VS AI: ' + ('ON' if self.play_vs_ai else 'OFF'))
        ]
        
        for i, (key, label) in enumerate(buttons_info):
            btn_rect = self.buttons[key]
            pygame.draw.rect(self.screen, BUTTON_COLOR, btn_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, btn_rect, 2)
            
            text = self.font_small.render(label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
        
        # AI status and move evaluation
        y_offset = 340
        if self.ai_thinking:
            ai_text = self.font_small.render("AI thinking...", True, (255, 0, 0))
            self.screen.blit(ai_text, (CONTROL_PANEL_X + 10, y_offset))
        elif self.last_ai_move:
            # Display AI move with centipawn evaluation
            ai_text = self.font_small.render(f"AI Move: {self.last_ai_move}", True, (0, 0, 200))
            self.screen.blit(ai_text, (CONTROL_PANEL_X + 10, y_offset))
            
            if self.last_ai_eval is not None:
                # Convert evaluation to centipawns for display
                centipawns = int(self.last_ai_eval * 100)
                eval_text = self.font_small.render(f"Eval: {centipawns} cp ({self.last_ai_eval:.2f})", True, (0, 0, 200))
                self.screen.blit(eval_text, (CONTROL_PANEL_X + 10, y_offset + 15))
        
        # Stockfish comparison with detailed centipawn values
        if self.stockfish_comparison:
            y_offset += 50
            comp_text = self.font_small.render("Stockfish Analysis:", True, TEXT_COLOR)
            self.screen.blit(comp_text, (CONTROL_PANEL_X + 10, y_offset))
            
            # Show user move ranking if available
            if self.stockfish_comparison.get('user_rank'):
                rank_text = self.font_small.render(f"Your move ranks #{self.stockfish_comparison['user_rank']}", True, (0, 150, 0))
                self.screen.blit(rank_text, (CONTROL_PANEL_X + 10, y_offset + 15))
                y_offset += 15
            
            # Display top 3 moves with centipawn values
            for i, move_data in enumerate(self.stockfish_comparison.get('top_moves', [])[:3]):
                y_pos = y_offset + 15 + (i * 15)
                
                # Format move with centipawn value
                move_text = f"{i+1}. {move_data['move']}"
                
                if move_data['centipawn'] is not None:
                    cp = move_data['centipawn']
                    pawns = cp / 100.0
                    move_text += f" ({cp:+d} cp / {pawns:+.1f})"
                elif move_data.get('mate') is not None:
                    mate_in = move_data['mate']
                    move_text += f" (Mate in {abs(mate_in)})"
                
                # Color coding for move ranking
                color = TEXT_COLOR
                if (self.stockfish_comparison.get('user_rank') == i + 1):
                    color = (0, 150, 0)  # Green for user's move
                elif i == 0:
                    color = (100, 100, 255)  # Light blue for best move
                
                text = self.font_small.render(move_text, True, color)
                self.screen.blit(text, (CONTROL_PANEL_X + 10, y_pos))
    
    def get_square_from_pos(self, pos):
        """Convert mouse position to chess square (accounting for board offset)"""
        x, y = pos
        # Adjust for board offset
        board_x = x - BOARD_OFFSET_X
        board_y = y - BOARD_OFFSET_Y
        
        # Check if click is within board bounds
        if board_x < 0 or board_x >= BOARD_SIZE or board_y < 0 or board_y >= BOARD_SIZE:
            return None
            
        file = board_x // SQUARE_SIZE
        rank = 7 - (board_y // SQUARE_SIZE)
        return chess.square(file, rank)
    
    def is_valid_move(self, from_square, to_square):
        """Check if a move is valid in current mode"""
        if self.current_mode == SETUP_MODE:
            # In setup mode, allow any placement except capturing kings
            target_piece = self.board.piece_at(to_square)
            if target_piece and target_piece.piece_type == chess.KING:
                return False
            return True
        else:
            # In play/analysis mode, only allow legal moves
            try:
                move = chess.Move(from_square, to_square)
                return move in self.board.legal_moves
            except:
                return False
    
    def make_move(self, move):
        """Make a move and update game state"""
        if move in self.board.legal_moves:
            self.move_history.append(move)
            self.position_history.append(self.board.fen())
            self.board.push(move)
            
            # Get Stockfish comparison for the move
            if self.stockfish_ai:
                self.get_stockfish_comparison(str(move))
            
            return True
        return False
    
    def get_ai_move(self):
        """Get AI move in background thread using notebook approach"""
        if not self.stockfish_ai:
            print("❌ Stockfish AI not available!")
            print("Install with: pip install stockfish")
            # Show message in GUI
            self.last_ai_move = "No AI available"
            self.last_ai_eval = None
            return
            
        if self.ai_thinking:
            print("AI is already thinking... canceling previous request")
            self.ai_thinking = False  # Cancel previous request
            time.sleep(0.1)  # Brief pause
        
        def ai_worker():
            self.ai_thinking = True
            try:
                # Use notebook approach with faster depth
                self.stockfish_ai.set_depth(8)  # Faster calculation
                self.stockfish_ai.set_fen_position(self.board.fen())
                
                # Get top moves (aim for 10th best as specified)
                top_moves = self.stockfish_ai.get_top_moves(12)
                
                if not top_moves:
                    print("No moves returned from Stockfish")
                    self.last_ai_move = "No moves"
                    self.last_ai_eval = None
                    return
                
                # Select 10th best move as requested, or fallback to available moves
                move_index = min(9, len(top_moves) - 1)  # 10th best (0-indexed) or last available
                selected_move = top_moves[move_index]
                
                move_uci = selected_move['Move']
                centipawns = selected_move['Centipawn'] if selected_move['Centipawn'] else 0
                eval_pawns = centipawns / 100.0
                
                self.last_ai_move = move_uci
                self.last_ai_eval = eval_pawns
                
                # Set AI suggested square for highlighting
                try:
                    ai_move_obj = chess.Move.from_uci(move_uci)
                    self.ai_suggested_square = ai_move_obj.to_square
                except:
                    self.ai_suggested_square = None
                
                # Print to console for debugging
                print(f"AI suggests: {move_uci} (rank {move_index + 1}, eval: {eval_pawns:.2f})")
                
                if self.current_mode == PLAY_MODE and self.play_vs_ai:
                    # Make the AI move
                    try:
                        ai_move = chess.Move.from_uci(move_uci)
                        if ai_move in self.board.legal_moves:
                            self.make_move(ai_move)
                            print(f"AI played: {move_uci}")
                    except Exception as e:
                        print(f"Error making AI move: {e}")
                
            except Exception as e:
                print(f"AI error: {e}")
                self.last_ai_move = "AI Error"
                self.last_ai_eval = None
            finally:
                self.ai_thinking = False
        
        threading.Thread(target=ai_worker, daemon=True).start()
    
    def get_stockfish_comparison(self, user_move):
        """Get Stockfish comparison for a move using notebook approach"""
        if not self.stockfish_ai:
            return
        
        def comparison_worker():
            try:
                # Create a copy of the board before the move
                temp_board = self.board.copy()
                temp_board.pop()  # Undo the last move
                
                # Set position and get top moves
                self.stockfish_ai.set_fen_position(temp_board.fen())
                top_moves = self.stockfish_ai.get_top_moves(5)
                
                # Find user move ranking
                user_rank = None
                for i, move_data in enumerate(top_moves):
                    if move_data['Move'] == user_move:
                        user_rank = i + 1
                        break
                
                # Convert to our format
                formatted_moves = []
                for move_data in top_moves:
                    formatted_moves.append({
                        'move': move_data['Move'],
                        'centipawn': move_data['Centipawn'],
                        'mate': None  # stockfish library doesn't provide mate info in top_moves
                    })
                
                self.stockfish_comparison = {
                    'user_rank': user_rank,
                    'top_moves': formatted_moves,
                    'user_move': user_move
                }
                
            except Exception as e:
                print(f"Stockfish comparison error: {e}")
        
        threading.Thread(target=comparison_worker, daemon=True).start()
    
    def handle_button_click(self, pos):
        """Handle clicks on control panel buttons"""
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(pos):
                if button_name.endswith('_mode'):
                    mode = button_name.replace('_mode', '')
                    self.current_mode = mode
                    self.valid_moves.clear()
                
                elif button_name == 'white_to_move':
                    self.active_color = chess.WHITE
                    self.board.turn = chess.WHITE
                
                elif button_name == 'black_to_move':
                    self.active_color = chess.BLACK
                    self.board.turn = chess.BLACK
                
                elif button_name in self.castling_rights:
                    self.castling_rights[button_name] = not self.castling_rights[button_name]
                
                elif button_name == 'clear_board':
                    self.board = chess.Board(fen=None)  # Empty board
                    self.move_history.clear()
                    self.position_history.clear()
                    self.stockfish_comparison = None
                    self.last_ai_move = None
                    print("Board cleared")
                
                elif button_name == 'reset_position':
                    self.board = chess.Board()  # Starting position
                    self.move_history.clear()
                    self.position_history.clear()
                    self.stockfish_comparison = None
                    self.last_ai_move = None
                    print("Position reset to starting position")
                
                elif button_name == 'get_best_move':
                    print("Getting AI move recommendation...")
                    self.get_ai_move()
                
                elif button_name == 'toggle_vs_ai':
                    self.play_vs_ai = not self.play_vs_ai
                    print(f"VS AI mode: {'ON' if self.play_vs_ai else 'OFF'}")
                
                return True
        return False
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check if click is on control panel
                        if event.pos[0] >= CONTROL_PANEL_X:
                            self.handle_button_click(event.pos)
                        else:
                            # Click on board
                            square = self.get_square_from_pos(event.pos)
                            if square is not None:
                                # In setup mode, allow selecting any square
                                # In other modes, only select squares with pieces of current player
                                piece = self.board.piece_at(square)
                                
                                if self.current_mode == SETUP_MODE:
                                    # In setup mode, select any piece
                                    if piece:
                                        self.selected_piece = square
                                        self.dragging = True
                                elif piece and piece.color == self.board.turn:
                                    # In play/analysis mode, only select pieces of current player
                                    self.selected_piece = square
                                    self.dragging = True
                                    self.valid_moves = {
                                        move.to_square 
                                        for move in self.board.legal_moves 
                                        if move.from_square == square
                                    }
                                else:
                                    # Clear selection if invalid piece clicked
                                    self.selected_piece = None
                                    self.valid_moves.clear()
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        target_square = self.get_square_from_pos(event.pos)
                        if target_square is not None:
                            if self.is_valid_move(self.selected_piece, target_square):
                                if self.current_mode == SETUP_MODE:
                                    # In setup mode, just move pieces
                                    piece = self.board.remove_piece_at(self.selected_piece)
                                    self.board.remove_piece_at(target_square)
                                    self.board.set_piece_at(target_square, piece)
                                else:
                                    # In play/analysis mode, make legal moves
                                    move = chess.Move(self.selected_piece, target_square)
                                    if self.make_move(move):
                                        # If playing vs AI and it's AI's turn
                                        if (self.current_mode == PLAY_MODE and 
                                            self.play_vs_ai and 
                                            self.board.turn != self.active_color):
                                            self.get_ai_move()
                        
                        self.dragging = False
                        self.selected_piece = None
                        self.valid_moves.clear()
            
            # Draw everything
            self.screen.fill((255, 255, 255))
            self.draw_board()
            self.draw_pieces()
            self.draw_control_panel()
            
            # Draw dragged piece
            if self.dragging:
                piece = self.board.piece_at(self.selected_piece)
                if piece:
                    color = 'w' if piece.color else 'b'
                    piece_key = f"{color}{piece.symbol().upper()}"
                    x, y = pygame.mouse.get_pos()
                    x -= PIECE_SIZE // 2
                    y -= PIECE_SIZE // 2
                    self.screen.blit(self.pieces[piece_key], (x, y))
            
            pygame.display.flip()
            clock.tick(60)
        
        # Cleanup
        if self.stockfish_ai:
            # Stockfish library handles cleanup automatically
            pass
        pygame.quit()

if __name__ == "__main__":
    print("ChessPredictor-Proto v1.0")
    print("Initializing...")
    
    try:
        app = ChessPredictor(use_svg=True)
        print("🚀 Starting ChessPredictor with enhanced board and AI...")
        print("Features:")
        print("✓ Professional chess board with a-h, 1-8 labels")
        print("✓ Stockfish AI integration")
        print("✓ VS AI mode available")
        print("✓ Real-time move analysis")
        print("\nClose window to exit")
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()