#!/usr/bin/env python3
"""
בדיקות פשוטות למשחק השחמט
Simple tests for the chess game
"""

import sys
import os

# Add current directory to path to import chess_game
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chess_game import ChessGame

def test_board_initialization():
    """Test that the board is initialized correctly"""
    game = ChessGame()
    
    # Check white pieces are in correct positions
    assert game.board[7][0] == ('white', 'rook'), "White rook should be at a1"
    assert game.board[7][4] == ('white', 'king'), "White king should be at e1"
    assert game.board[6][0] == ('white', 'pawn'), "White pawn should be at a2"
    
    # Check black pieces are in correct positions
    assert game.board[0][0] == ('black', 'rook'), "Black rook should be at a8"
    assert game.board[0][4] == ('black', 'king'), "Black king should be at e8"
    assert game.board[1][0] == ('black', 'pawn'), "Black pawn should be at a7"
    
    print("✅ Board initialization test passed")

def test_pawn_movement():
    """Test basic pawn movement"""
    game = ChessGame()
    
    # Test white pawn double move from starting position
    assert game.is_valid_move((6, 0), (4, 0)), "White pawn should be able to move two squares"
    assert game.is_valid_move((6, 0), (5, 0)), "White pawn should be able to move one square"
    
    # Test black pawn movement
    assert game.is_valid_move((1, 0), (3, 0)), "Black pawn should be able to move two squares"
    assert game.is_valid_move((1, 0), (2, 0)), "Black pawn should be able to move one square"
    
    print("✅ Pawn movement test passed")

def test_piece_movement():
    """Test basic piece movement patterns"""
    game = ChessGame()
    
    # Clear some squares for testing
    game.board[6][1] = None  # Remove white pawn
    game.board[1][1] = None  # Remove black pawn
    
    # Test knight movement
    assert game.is_valid_move((7, 1), (5, 2)), "Knight should move in L-shape"
    assert game.is_valid_move((0, 1), (2, 2)), "Black knight should move in L-shape"
    
    print("✅ Piece movement test passed")

def test_invalid_moves():
    """Test that invalid moves are rejected"""
    game = ChessGame()
    
    # Test moving to same square
    assert not game.is_valid_move((6, 0), (6, 0)), "Can't move to same square"
    
    # Test moving to square with own piece
    assert not game.is_valid_move((6, 0), (7, 0)), "Can't capture own piece"
    
    # Test invalid pawn move (moving backwards)
    assert not game.is_valid_move((6, 0), (7, 0)), "Pawn can't move backwards"
    
    # Test moving piece that doesn't exist
    game.board[4][4] = None
    assert not game.is_valid_move((4, 4), (5, 5)), "Can't move piece that doesn't exist"
    
    print("✅ Invalid moves test passed")

def test_check_detection():
    """Test check detection"""
    game = ChessGame()
    
    # Create a simple check scenario
    game.board = [[None for _ in range(8)] for _ in range(8)]
    game.board[0][4] = ('black', 'king')
    game.board[7][4] = ('white', 'rook')
    
    assert game.is_in_check('black'), "Black king should be in check from white rook"
    assert not game.is_in_check('white'), "White should not be in check"
    
    print("✅ Check detection test passed")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting chess game tests...")
    print()
    
    try:
        test_board_initialization()
        test_pawn_movement()
        test_piece_movement()
        test_invalid_moves()
        test_check_detection()
        
        print()
        print("🎉 All tests passed! The chess game is working correctly.")
        print("🎮 You can now run: python chess_game.py")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests() 