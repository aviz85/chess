import tkinter as tk
from tkinter import messagebox
import copy

class ChessGame:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.game_over = False
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.en_passant_target = None
        self.move_history = []
        self.moves_since_capture = 0
        self.position_history = []
        self.save_position()

    def create_initial_board(self):
        """Create the initial chess board setup"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place pawns
        for col in range(8):
            board[1][col] = ('black', 'pawn')
            board[6][col] = ('white', 'pawn')
        
        # Place other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col in range(8):
            board[0][col] = ('black', piece_order[col])
            board[7][col] = ('white', piece_order[col])
            
        return board

    def get_game_state(self):
        """Return the current game state as a dictionary"""
        return {
            'board': self.board,
            'currentPlayer': self.current_player,
            'gameOver': self.game_over,
            'check': self.is_in_check(self.current_player),
            'checkmate': self.is_checkmate(self.current_player),
            'stalemate': self.is_stalemate(self.current_player)
        }

# Create global game instance
game = ChessGame()

@app.route('/game-state', methods=['GET'])
def get_game_state():
    return jsonify(game.get_game_state())

@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    from_pos = tuple(data['from'])
    to_pos = tuple(data['to'])
    
    if game.is_valid_move(from_pos, to_pos):
        game.make_move(from_pos, to_pos)
        game.switch_player()
        return jsonify({'success': True, 'gameState': game.get_game_state()})
    return jsonify({'success': False, 'message': 'Invalid move'})

@app.route('/reset', methods=['POST'])
def reset_game():
    global game
    game = ChessGame()
    return jsonify({'success': True, 'gameState': game.get_game_state()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)