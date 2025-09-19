# ChessPredictor-Proto v1.0

A prototype chess AI that predicts the next best move using Stockfish integration and provides move analysis. Built as a demonstration of rapid prototyping for chess AI applications.

## Features

- 🎯 **Three Game Modes**: Setup, Analysis, and Play modes
- 🤖 **AI Integration**: Uses Stockfish as backup AI engine
- 📊 **Move Analysis**: Compare moves with Stockfish's top recommendations
- 🎮 **Interactive GUI**: Drag-and-drop piece movement with visual feedback
- ⚙️ **Customizable Setup**: Adjust board position, castling rights, and active color
- 🔄 **Dataset Processing**: Parse Lichess Elite Database for future training

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd d:\chess

# Run the setup script (installs dependencies and downloads Stockfish)
python setup_prototype.py
```

### 2. Manual Setup (if needed)

```bash
# Install required packages
pip install chess pygame numpy

# Ensure piece files are in pieces/svg/ directory
# Download from: https://github.com/lichess-org/lila/tree/master/public/piece

# Download Stockfish binary from: https://stockfishchess.org/download/
# Place as stockfish.exe in the project directory
```

### 3. Run the Application

```bash
python chess_predictor.py
```

## File Structure

```
d:\chess\
├── chess_predictor.py      # Main application
├── stockfish_ai.py         # Stockfish AI integration
├── dataset_processor.py    # Lichess dataset processing
├── config.py              # Configuration and constants
├── eval.py                # Basic position evaluation
├── setup_prototype.py     # Setup and testing script
├── pieces/
│   └── svg/               # Chess piece sprites
│       ├── wK.svg, wQ.svg, etc.
│       └── bK.svg, bQ.svg, etc.
├── stockfish.exe          # Stockfish engine binary
└── README.md             # This file
```

## Usage Guide

### Game Modes

1. **Setup Mode**: 
   - Drag pieces freely to set up any position
   - Modify castling rights and active color
   - Perfect for analyzing specific positions

2. **Analysis Mode**:
   - Make legal moves only
   - Get AI move suggestions
   - Compare moves with Stockfish analysis

3. **Play Mode**:
   - Play against AI or analyze games
   - Enable "VS AI" to play against Stockfish
   - Full move validation and game rules

### Control Panel

- **Game Mode**: Switch between Setup, Analysis, and Play
- **Active Color**: Set who's turn it is to move
- **Castling Rights**: Enable/disable castling for each side
- **Actions**:
  - Clear Board: Remove all pieces
  - Reset Position: Return to starting position
  - Get Best Move: Ask AI for move suggestion
  - VS AI: Toggle playing against AI

### AI Features

- **Move Prediction**: Uses Stockfish's 2nd best move as AI response
- **Move Comparison**: Shows top 3 Stockfish moves after each move
- **Evaluation**: Displays position evaluation in centipawns/pawns
- **Ranking**: Shows how your move ranks compared to engine

## Dataset Processing

Process Lichess Elite Database for training data:

```python
from dataset_processor import DatasetProcessor

# Point to your downloaded Lichess PGN file(s)
processor = DatasetProcessor("path/to/lichess_elite_2025-01.pgn")

# Create sample dataset (5000 positions)
stats = processor.create_sample_dataset(
    sample_size=5000, 
    output_file="training_positions.csv"
)
```

## Development Timeline (PRD Implementation)

This prototype was designed to be built in under 12 hours following the PRD:

- ✅ **Hours 0-3**: Stockfish integration and dataset processing
- ✅ **Hours 3-6**: GUI development and game logic
- ✅ **Hours 6-9**: Move comparison and AI integration
- ✅ **Hours 9-12**: Testing, polish, and documentation

## Technical Architecture

### Core Components

1. **ChessPredictor**: Main application class
   - GUI rendering and event handling
   - Game state management
   - Mode switching logic

2. **StockfishAI**: Engine integration
   - Move generation and evaluation
   - Multi-threaded analysis
   - Move ranking and comparison

3. **DatasetProcessor**: Training data preparation
   - PGN file parsing
   - Position extraction
   - High-quality game filtering

### Dependencies

- `python-chess`: Chess game logic and PGN parsing
- `pygame`: GUI and graphics
- `numpy`: Numerical operations
- Stockfish binary: Chess engine

## Performance

- **Move Generation**: <1s per move
- **GUI**: 60 FPS rendering
- **Dataset Processing**: ~1000 positions/second
- **Memory Usage**: ~100MB typical

## Future Enhancements (Phase 2)

- Custom neural network training on processed dataset
- NNUE (Efficiently Updatable Neural Network) integration
- Opening book and endgame tablebase support
- Advanced position evaluation features
- Tournament analysis tools

## Troubleshooting

### Common Issues

1. **"Stockfish not found"**
   - Download from https://stockfishchess.org/download/
   - Place binary as `stockfish.exe` in project directory
   - Or specify path in code: `StockfishAI("/path/to/stockfish")`

2. **"Missing piece files"**
   - Ensure pieces/svg/ directory exists
   - Download SVG pieces from Lichess repository
   - Use standard naming: wK.svg, bQ.svg, etc.

3. **"Module not found"**
   - Run: `pip install chess pygame numpy`
   - Check Python version (3.8+ required)

4. **Performance issues**
   - Reduce Stockfish depth in stockfish_ai.py
   - Disable AI features if hardware is limited

### Debug Mode

Enable debug output:

```python
# In chess_predictor.py
app = ChessPredictor(use_svg=True, stockfish_path="stockfish.exe")
app.debug = True  # Add this line
app.run()
```

## Contributing

This is a prototype built for demonstration purposes. For improvements:

1. Fork the repository
2. Make changes following the existing code style
3. Test thoroughly with `python setup_prototype.py`
4. Submit pull request with description

## License

This project is for educational and demonstration purposes. 

- Chess piece graphics: Lichess (https://lichess.org) - GPL v3+
- Stockfish engine: Stockfish project - GPL v3+
- Code: MIT License

## Acknowledgments

- Stockfish team for the chess engine
- Lichess for open-source chess pieces and database
- Python-chess library for chess logic
- Pygame for graphics framework

---

**Built with ❤️ for rapid chess AI prototyping**