import chess
import pygame
import pygame.gfxdraw
from config import *

class ChessGUI:
    def __init__(self, use_svg=True):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess Analysis Board")
        
        # Validate and load pieces
        if not validate_piece_files(use_svg):
            pygame.quit()
            exit(1)
            
        self.pieces = {}
        self.load_pieces(use_svg)
        
        self.board = chess.Board()
        self.selected_piece = None
        self.dragging = False
        self.setup_mode = True
        self.valid_moves = set()
        
    def load_pieces(self, use_svg):
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

    def draw_board(self):
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )
        
        # Draw valid move dots
        if self.selected_piece and not self.setup_mode:
            for move in self.valid_moves:
                center_x = (chess.square_file(move) * SQUARE_SIZE) + SQUARE_SIZE // 2
                center_y = (7 - chess.square_rank(move)) * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.gfxdraw.filled_circle(
                    self.screen, center_x, center_y, 
                    SQUARE_SIZE // 6, VALID_MOVE_DOT
                )

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'w' if piece.color else 'b'
                piece_key = f"{color}{piece.symbol().upper()}"
                x = chess.square_file(square) * SQUARE_SIZE + PIECE_OFFSET
                y = (7 - chess.square_rank(square)) * SQUARE_SIZE + PIECE_OFFSET
                
                # Don't draw the piece being dragged
                if self.dragging and self.selected_piece == square:
                    continue
                    
                self.screen.blit(self.pieces[piece_key], (x, y))

    def get_square_from_pos(self, pos):
        x, y = pos
        if x >= BOARD_SIZE or y >= BOARD_SIZE:
            return None
        file = x // SQUARE_SIZE
        rank = 7 - (y // SQUARE_SIZE)
        return chess.square(file, rank)

    def is_valid_move(self, from_square, to_square):
        if self.setup_mode:
            # In setup mode, allow any placement except:
            # 1. Can't place pieces outside the board
            # 2. Can't capture own king (to prevent invalid positions)
            target_piece = self.board.piece_at(to_square)
            moving_piece = self.board.piece_at(from_square)
            if target_piece and target_piece.piece_type == chess.KING:
                return False
            return True
        else:
            # In play mode, only allow legal moves
            move = chess.Move(from_square, to_square)
            return move in self.board.legal_moves

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        square = self.get_square_from_pos(event.pos)
                        if square is not None and self.board.piece_at(square):
                            self.selected_piece = square
                            self.dragging = True
                            if not self.setup_mode:
                                self.valid_moves = {
                                    move.to_square 
                                    for move in self.board.legal_moves 
                                    if move.from_square == square
                                }
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging:
                        target_square = self.get_square_from_pos(event.pos)
                        if target_square is not None:
                            if self.is_valid_move(self.selected_piece, target_square):
                                piece = self.board.remove_piece_at(self.selected_piece)
                                # If there's a piece at target, remove it (capture/replace)
                                self.board.remove_piece_at(target_square)
                                self.board.set_piece_at(target_square, piece)
                            else:
                                # Invalid move - piece snaps back
                                pass
                        self.dragging = False
                        self.selected_piece = None
                        self.valid_moves.clear()

            # Draw everything
            self.screen.fill((255, 255, 255))
            self.draw_board()
            self.draw_pieces()
            
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

        pygame.quit()

if __name__ == "__main__":
    gui = ChessGUI(use_svg=True)  # Changed to True to use SVG files
    gui.run()