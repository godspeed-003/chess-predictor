#!/usr/bin/env python3
"""
Quick test for ChessPredictor components
"""

import chess
from stockfish_ai import StockfishAI

def test_stockfish_basic():
    """Test basic Stockfish functionality"""
    try:
        print("Testing Stockfish AI...")
        ai = StockfishAI("stockfish.exe")
        board = chess.Board()
        
        # Test getting best moves
        moves = ai.get_best_moves(board, 8)
        print(f"Found {len(moves)} moves from starting position:")
        for i, move in enumerate(moves[:5]):
            cp = move['centipawn'] / 100.0 if move['centipawn'] else 0.0
            print(f"  {i+1}. {move['move']} ({cp:.2f})")
        
        # Test AI prediction (6th best move)
        ai_move, eval_score = ai.ai_predict_backup(board, 6)
        print(f"\nAI recommendation (6th best): {ai_move} ({eval_score:.2f})")
        
        # Test comparison
        comparison = ai.compare_move_to_engine(board, "e2e4")
        print(f"\nMove e2e4 ranking: {comparison['user_rank']}")
        
        ai.close()
        print("✓ Stockfish AI test passed")
        return True
        
    except Exception as e:
        print(f"✗ Stockfish AI test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components"""
    try:
        print("\nTesting GUI components...")
        import config
        print(f"Window size: {config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        print(f"Board size: {config.BOARD_SIZE}x{config.BOARD_SIZE}")
        print(f"Square size: {config.SQUARE_SIZE}px")
        print(f"Piece size: {config.PIECE_SIZE}px")
        print("✓ GUI config test passed")
        return True
        
    except Exception as e:
        print(f"✗ GUI config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("ChessPredictor Component Test")
    print("=" * 30)
    
    success = True
    
    # Test Stockfish
    success &= test_stockfish_basic()
    
    # Test GUI config
    success &= test_gui_components()
    
    print("\n" + "=" * 30)
    if success:
        print("✓ All tests passed! ChessPredictor should work.")
        print("\nTo run the full application:")
        print("python chess_predictor.py")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()