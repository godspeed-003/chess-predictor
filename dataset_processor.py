import chess.pgn
import json
import csv
from pathlib import Path
from typing import List, Dict, Generator, Optional
import time

class DatasetProcessor:
    def __init__(self, dataset_path: str):
        """
        Initialize dataset processor for Lichess Elite Database
        
        Args:
            dataset_path: Path to directory containing PGN files
        """
        self.dataset_path = Path(dataset_path)
        self.processed_games = 0
        self.processed_positions = 0
    
    def find_pgn_files(self) -> List[Path]:
        """Find all PGN files in the dataset directory"""
        pgn_files = []
        
        if self.dataset_path.is_file() and self.dataset_path.suffix == '.pgn':
            pgn_files.append(self.dataset_path)
        elif self.dataset_path.is_dir():
            pgn_files.extend(self.dataset_path.glob('*.pgn'))
            pgn_files.extend(self.dataset_path.glob('**/*.pgn'))
        
        return sorted(pgn_files)
    
    def parse_game(self, game: chess.pgn.Game) -> Optional[Dict]:
        """
        Parse a single game and extract metadata
        
        Returns:
            Dict with game info or None if game should be skipped
        """
        headers = game.headers
        
        # Filter for high-quality games
        try:
            white_elo = int(headers.get('WhiteElo', 0))
            black_elo = int(headers.get('BlackElo', 0))
            
            # Only process games with both players > 2400 Elo
            if white_elo < 2400 or black_elo < 2400:
                return None
            
            # Skip bullet/blitz games (focus on classical)
            time_control = headers.get('TimeControl', '')
            if '+' in time_control:
                base_time = int(time_control.split('+')[0])
                if base_time < 600:  # Less than 10 minutes
                    return None
            
            return {
                'white': headers.get('White', 'Unknown'),
                'black': headers.get('Black', 'Unknown'),
                'white_elo': white_elo,
                'black_elo': black_elo,
                'result': headers.get('Result', '*'),
                'date': headers.get('Date', ''),
                'event': headers.get('Event', ''),
                'time_control': time_control,
                'opening': headers.get('Opening', ''),
                'eco': headers.get('ECO', '')
            }
        except (ValueError, TypeError):
            return None
    
    def extract_positions(self, game: chess.pgn.Game) -> Generator[Dict, None, None]:
        """
        Extract training positions from a game
        
        Yields:
            Dict with position data (FEN, move, evaluation)
        """
        board = game.board()
        move_number = 0
        
        for move in game.mainline_moves():
            move_number += 1
            
            # Skip opening moves (first 10 moves)
            if move_number <= 10:
                board.push(move)
                continue
            
            # Skip endgame positions (less than 10 pieces)
            if len(board.piece_map()) < 10:
                board.push(move)
                continue
            
            # Record position before move
            position_data = {
                'fen': board.fen(),
                'move': move.uci(),
                'move_san': board.san(move),
                'move_number': move_number,
                'to_move': 'white' if board.turn else 'black',
                'evaluation': self._evaluate_position(board),
                'piece_count': len(board.piece_map())
            }
            
            board.push(move)
            yield position_data
    
    def _evaluate_position(self, board: chess.Board) -> float:
        """
        Simple material evaluation in centipawns
        """
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }
        
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
        
        # Return from white's perspective
        return (white_material - black_material) / 100.0
    
    def process_files(self, max_games: int = 1000, output_file: str = None) -> Dict:
        """
        Process PGN files and extract training data
        
        Args:
            max_games: Maximum number of games to process
            output_file: Optional CSV file to save positions
            
        Returns:
            Dict with processing statistics
        """
        pgn_files = self.find_pgn_files()
        
        if not pgn_files:
            raise FileNotFoundError(f"No PGN files found in {self.dataset_path}")
        
        print(f"Found {len(pgn_files)} PGN file(s)")
        
        all_positions = []
        processed_games = 0
        skipped_games = 0
        start_time = time.time()
        
        # Setup CSV writer if output file specified
        csv_writer = None
        csv_file = None
        if output_file:
            csv_file = open(output_file, 'w', newline='', encoding='utf-8')
            fieldnames = ['fen', 'move', 'move_san', 'move_number', 'to_move', 'evaluation', 'piece_count']
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
        
        try:
            for pgn_file in pgn_files:
                print(f"Processing {pgn_file.name}...")
                
                with open(pgn_file, 'r', encoding='utf-8') as f:
                    while processed_games < max_games:
                        game = chess.pgn.read_game(f)
                        if game is None:
                            break
                        
                        game_info = self.parse_game(game)
                        if game_info is None:
                            skipped_games += 1
                            continue
                        
                        # Extract positions from this game
                        game_positions = list(self.extract_positions(game))
                        
                        # Add to collection
                        all_positions.extend(game_positions)
                        
                        # Write to CSV if specified
                        if csv_writer:
                            csv_writer.writerows(game_positions)
                        
                        processed_games += 1
                        
                        if processed_games % 100 == 0:
                            elapsed = time.time() - start_time
                            print(f"Processed {processed_games} games, {len(all_positions)} positions in {elapsed:.1f}s")
                
                if processed_games >= max_games:
                    break
        
        finally:
            if csv_file:
                csv_file.close()
        
        elapsed_time = time.time() - start_time
        
        stats = {
            'processed_games': processed_games,
            'skipped_games': skipped_games,
            'total_positions': len(all_positions),
            'processing_time': elapsed_time,
            'positions_per_second': len(all_positions) / elapsed_time if elapsed_time > 0 else 0,
            'pgn_files_processed': len(pgn_files)
        }
        
        print(f"\nDataset processing completed:")
        print(f"- Processed: {processed_games} games")
        print(f"- Skipped: {skipped_games} games")
        print(f"- Positions: {len(all_positions)}")
        print(f"- Time: {elapsed_time:.1f}s")
        print(f"- Rate: {stats['positions_per_second']:.1f} positions/second")
        
        return stats
    
    def create_sample_dataset(self, sample_size: int = 10000, output_file: str = "chess_positions_sample.csv"):
        """
        Create a sample dataset for quick testing
        """
        print(f"Creating sample dataset with {sample_size} positions...")
        
        # Process enough games to get the sample size
        estimated_games = sample_size // 20  # Roughly 20 positions per game
        
        stats = self.process_files(max_games=estimated_games, output_file=output_file)
        
        print(f"Sample dataset saved to {output_file}")
        return stats

# Test/demo function
if __name__ == "__main__":
    # Example usage
    dataset_path = input("Enter path to Lichess dataset (PGN file or directory): ").strip()
    
    if not dataset_path:
        print("No path provided, exiting...")
        exit()
    
    try:
        processor = DatasetProcessor(dataset_path)
        
        # Create a sample dataset
        stats = processor.create_sample_dataset(
            sample_size=5000, 
            output_file=r"d:\chess\training_positions.csv"
        )
        
        print("\nDataset processing completed successfully!")
        print("You can now use the training_positions.csv file for model training.")
        
    except Exception as e:
        print(f"Error processing dataset: {e}")