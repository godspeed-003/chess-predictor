#!/usr/bin/env python3
"""
Manual Stockfish installer and tester
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def manual_stockfish_install():
    """Manually install Stockfish with detailed steps"""
    print("Manual Stockfish Installation")
    print("=" * 40)
    
    # Check if already exists
    if Path("stockfish.exe").exists():
        print("✓ stockfish.exe already exists")
        if test_stockfish("stockfish.exe"):
            return "stockfish.exe"
        else:
            print("✗ Existing stockfish.exe doesn't work, re-downloading...")
    
    print("\n1. Downloading latest Stockfish...")
    try:
        # Download SF 16 (latest stable)
        url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-windows-x86-64-avx2.zip"
        print(f"URL: {url}")
        
        urllib.request.urlretrieve(url, "stockfish_download.zip")
        print("✓ Download completed")
        
        print("\n2. Extracting files...")
        with zipfile.ZipFile("stockfish_download.zip", 'r') as zip_ref:
            zip_ref.extractall("stockfish_extracted")
        
        print("\n3. Looking for executable...")
        # Find the stockfish executable
        extracted_dir = Path("stockfish_extracted")
        stockfish_exe = None
        
        for file_path in extracted_dir.rglob("*"):
            print(f"Found: {file_path}")
            if (file_path.is_file() and 
                file_path.name.lower().startswith("stockfish") and 
                file_path.suffix.lower() == ".exe"):
                stockfish_exe = file_path
                print(f"✓ Found Stockfish executable: {stockfish_exe}")
                break
        
        if not stockfish_exe:
            print("✗ Could not find stockfish executable in downloaded files")
            print("Contents of extracted directory:")
            for item in extracted_dir.rglob("*"):
                print(f"  {item}")
            return None
        
        print("\n4. Copying to main directory...")
        import shutil
        shutil.copy(stockfish_exe, "stockfish.exe")
        
        print("\n5. Testing executable...")
        if test_stockfish("stockfish.exe"):
            print("✓ Stockfish installation successful!")
            
            # Cleanup
            shutil.rmtree("stockfish_extracted")
            os.remove("stockfish_download.zip")
            
            return "stockfish.exe"
        else:
            print("✗ Stockfish test failed")
            return None
            
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        print("\nManual installation steps:")
        print("1. Go to https://stockfishchess.org/download/")
        print("2. Download 'Windows' version")
        print("3. Extract the zip file")
        print("4. Copy the stockfish.exe to this directory")
        print("5. Run this script again to test")
        return None

def test_stockfish(path):
    """Test if Stockfish works"""
    try:
        print(f"Testing {path}...")
        result = subprocess.run(
            [path, "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0 and "stockfish" in result.stdout.lower():
            print("✓ Stockfish responds correctly")
            
            # Test UCI protocol
            print("Testing UCI protocol...")
            process = subprocess.Popen(
                [path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input="uci\nquit\n", timeout=5)
            if "uciok" in stdout:
                print("✓ UCI protocol working")
                return True
            else:
                print("✗ UCI protocol failed")
                print(f"Output: {stdout}")
                return False
        else:
            print("✗ Stockfish help command failed")
            print(f"Return code: {result.returncode}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Stockfish test timed out")
        return False
    except Exception as e:
        print(f"✗ Stockfish test error: {e}")
        return False

def test_with_chess():
    """Test Stockfish with chess integration"""
    try:
        print("\nTesting with chess library...")
        from stockfish_ai import StockfishAI
        import chess
        
        ai = StockfishAI("stockfish.exe")
        board = chess.Board()
        
        moves = ai.get_best_moves(board, 3)
        print(f"✓ Got {len(moves)} moves from starting position:")
        for i, move in enumerate(moves):
            cp = move['centipawn'] / 100.0 if move['centipawn'] else 0.0
            print(f"  {i+1}. {move['move']} ({cp:.2f})")
        
        ai.close()
        print("✓ Chess integration test passed")
        return True
        
    except Exception as e:
        print(f"✗ Chess integration test failed: {e}")
        return False

def cleanup_old_files():
    """Clean up old/unused files"""
    old_files = [
        "config_old_broken.py",
        "config_enhanced.py", 
        "stockfish_ai.py",
        "stockfish_simple.py",
        "test_notebook_stockfish.py",
        "test_updated_predictor.py", 
        "test_enhanced_board.py",
        "test_final.py",
        "test_stockfish_simple.py",
        "fix_config.py",
        "test_fixed_predictor.py",
        "setup_prototype.py"
    ]
    
    print("Cleaning up old files...")
    for file in old_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Deleted: {file}")
        else:
            print(f"- Not found: {file}")
    print("✅ Cleanup completed!")

def main():
    """Main installer function"""
    print("ChessPredictor Stockfish Installer")
    print("=" * 40)
    
    choice = input("What would you like to do?\n1. Install Stockfish\n2. Clean up old files\n3. Both\nChoice (1/2/3): ")
    
    if choice in ['2', '3']:
        cleanup_old_files()
        print()
    
    if choice in ['1', '3']:
        # Try to install Stockfish
        stockfish_path = manual_stockfish_install()
        
        if stockfish_path:
            print(f"\n✓ Stockfish installed at: {stockfish_path}")
            print("\n✅ Ready to run ChessPredictor!")
            print("\nRun: python chess_predictor.py")
        else:
            print("\n❌ Stockfish installation failed")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()