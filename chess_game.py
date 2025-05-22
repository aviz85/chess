import tkinter as tk
from tkinter import messagebox
import copy

class ChessGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Game - משחק שחמט")
        self.root.geometry("600x700")
        
        # Initialize board state
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.game_over = False
        
        # Special game states
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.en_passant_target = None
        self.move_history = []
        
        # Create GUI
        self.create_gui()
        
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
    
    def create_gui(self):
        """Create the graphical user interface"""
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)
        
        # Create info label
        self.info_label = tk.Label(main_frame, text=f"Current Player: {self.current_player.title()}", 
                                  font=("Arial", 14))
        self.info_label.pack(pady=10)
        
        # Create chess board
        self.board_frame = tk.Frame(main_frame, bg='brown')
        self.board_frame.pack()
        
        self.buttons = []
        for row in range(8):
            button_row = []
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                btn = tk.Button(self.board_frame, width=8, height=4, bg=color,
                               command=lambda r=row, c=col: self.on_square_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Create control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        reset_btn = tk.Button(control_frame, text="New Game", command=self.reset_game)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(control_frame, text="Quit", command=self.root.quit)
        quit_btn.pack(side=tk.LEFT, padx=5)
        
        # Update board display
        self.update_board_display()
    
    def update_board_display(self):
        """Update the visual representation of the board"""
        piece_symbols = {
            ('white', 'king'): '♔', ('white', 'queen'): '♕', ('white', 'rook'): '♖',
            ('white', 'bishop'): '♗', ('white', 'knight'): '♘', ('white', 'pawn'): '♙',
            ('black', 'king'): '♚', ('black', 'queen'): '♛', ('black', 'rook'): '♜',
            ('black', 'bishop'): '♝', ('black', 'knight'): '♞', ('black', 'pawn'): '♟'
        }
        
        for row in range(8):
            for col in range(8):
                btn = self.buttons[row][col]
                piece = self.board[row][col]
                
                # Reset background color
                base_color = 'white' if (row + col) % 2 == 0 else 'lightgray'
                
                # Highlight selected piece
                if self.selected_pos == (row, col):
                    base_color = 'yellow'
                elif self.selected_piece and self.is_valid_move(self.selected_pos, (row, col)):
                    base_color = 'lightgreen'
                
                btn.config(bg=base_color)
                
                # Set piece symbol
                if piece:
                    btn.config(text=piece_symbols.get(piece, ''), font=("Arial", 20))
                else:
                    btn.config(text='')
    
    def on_square_click(self, row, col):
        """Handle square click events"""
        if self.game_over:
            return
        
        if self.selected_piece is None:
            # Select a piece
            piece = self.board[row][col]
            if piece and piece[0] == self.current_player:
                self.selected_piece = piece
                self.selected_pos = (row, col)
        else:
            # Try to move the selected piece
            if self.selected_pos == (row, col):
                # Deselect
                self.selected_piece = None
                self.selected_pos = None
            elif self.is_valid_move(self.selected_pos, (row, col)):
                self.make_move(self.selected_pos, (row, col))
                self.selected_piece = None
                self.selected_pos = None
                self.switch_player()
                self.check_game_state()
            else:
                # Try to select a new piece of the same color
                piece = self.board[row][col]
                if piece and piece[0] == self.current_player:
                    self.selected_piece = piece
                    self.selected_pos = (row, col)
                else:
                    self.selected_piece = None
                    self.selected_pos = None
        
        self.update_board_display()
    
    def is_valid_move(self, from_pos, to_pos):
        """Check if a move is valid according to chess rules"""
        if not from_pos or not to_pos:
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check bounds
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        if not piece:
            return False
        
        color, piece_type = piece
        
        # Can't capture own pieces
        if target and target[0] == color:
            return False
        
        # Check piece-specific movement rules
        if not self.is_valid_piece_move(from_pos, to_pos, piece_type):
            return False
        
        # Check if path is clear (except for knights)
        if piece_type != 'knight' and not self.is_path_clear(from_pos, to_pos):
            return False
        
        # Check if move would put own king in check
        if self.would_be_in_check_after_move(from_pos, to_pos, color):
            return False
        
        return True
    
    def is_valid_piece_move(self, from_pos, to_pos, piece_type):
        """Check if move is valid for specific piece type"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if piece_type == 'pawn':
            return self.is_valid_pawn_move(from_pos, to_pos)
        elif piece_type == 'rook':
            return row_diff == 0 or col_diff == 0
        elif piece_type == 'bishop':
            return row_diff == col_diff and row_diff > 0
        elif piece_type == 'queen':
            return (row_diff == 0 or col_diff == 0) or (row_diff == col_diff and row_diff > 0)
        elif piece_type == 'king':
            return self.is_valid_king_move(from_pos, to_pos)
        elif piece_type == 'knight':
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
        
        return False
    
    def is_valid_pawn_move(self, from_pos, to_pos):
        """Check if pawn move is valid"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        color = piece[0]
        
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        # Forward move
        if from_col == to_col:
            if to_row == from_row + direction and not target:
                return True
            # Double move from starting position
            if from_row == start_row and to_row == from_row + 2 * direction and not target:
                return True
        
        # Diagonal capture
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            if target and target[0] != color:
                return True
            # En passant
            if self.en_passant_target == (to_row, to_col):
                return True
        
        return False
    
    def is_valid_king_move(self, from_pos, to_pos):
        """Check if king move is valid (including castling)"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # Normal king move
        if row_diff <= 1 and col_diff <= 1:
            return True
        
        # Castling
        if row_diff == 0 and col_diff == 2:
            return self.can_castle(from_pos, to_pos)
        
        return False
    
    def can_castle(self, king_pos, target_pos):
        """Check if castling is possible"""
        from_row, from_col = king_pos
        to_row, to_col = target_pos
        color = self.board[from_row][from_col][0]
        
        # King must not have moved
        if (color == 'white' and self.white_king_moved) or (color == 'black' and self.black_king_moved):
            return False
        
        # King must not be in check
        if self.is_in_check(color):
            return False
        
        # Determine castling side
        if to_col > from_col:  # Kingside
            rook_col = 7
            rook_moved = self.white_rook_h_moved if color == 'white' else self.black_rook_h_moved
            path_cols = [5, 6]
        else:  # Queenside
            rook_col = 0
            rook_moved = self.white_rook_a_moved if color == 'white' else self.black_rook_a_moved
            path_cols = [1, 2, 3]
        
        # Rook must not have moved
        if rook_moved:
            return False
        
        # Rook must be present
        rook = self.board[from_row][rook_col]
        if not rook or rook != (color, 'rook'):
            return False
        
        # Path must be clear
        for col in path_cols:
            if self.board[from_row][col]:
                return False
        
        # King must not pass through or end in check
        for col in [from_col + 1, from_col + 2] if to_col > from_col else [from_col - 1, from_col - 2]:
            temp_board = copy.deepcopy(self.board)
            temp_board[from_row][col] = temp_board[from_row][from_col]
            temp_board[from_row][from_col] = None
            if self.is_position_in_check(temp_board, (from_row, col), color):
                return False
        
        return True
    
    def is_path_clear(self, from_pos, to_pos):
        """Check if path between two positions is clear"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row, current_col = from_row + row_step, from_col + col_step
        
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def make_move(self, from_pos, to_pos):
        """Execute a move on the board"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        color, piece_type = piece
        
        # Handle special moves
        if piece_type == 'king':
            # Castling
            if abs(to_col - from_col) == 2:
                if to_col > from_col:  # Kingside
                    self.board[from_row][5] = self.board[from_row][7]
                    self.board[from_row][7] = None
                else:  # Queenside
                    self.board[from_row][3] = self.board[from_row][0]
                    self.board[from_row][0] = None
            
            # Update king moved flag
            if color == 'white':
                self.white_king_moved = True
            else:
                self.black_king_moved = True
        
        elif piece_type == 'rook':
            # Update rook moved flags
            if color == 'white':
                if from_col == 0:
                    self.white_rook_a_moved = True
                elif from_col == 7:
                    self.white_rook_h_moved = True
            else:
                if from_col == 0:
                    self.black_rook_a_moved = True
                elif from_col == 7:
                    self.black_rook_h_moved = True
        
        elif piece_type == 'pawn':
            # En passant capture
            if self.en_passant_target == (to_row, to_col):
                capture_row = to_row + (1 if color == 'white' else -1)
                self.board[capture_row][to_col] = None
            
            # Set en passant target for next turn
            if abs(to_row - from_row) == 2:
                self.en_passant_target = (from_row + (to_row - from_row) // 2, from_col)
            else:
                self.en_passant_target = None
            
            # Pawn promotion
            if (color == 'white' and to_row == 0) or (color == 'black' and to_row == 7):
                self.board[to_row][to_col] = (color, 'queen')  # Auto-promote to queen
                self.board[from_row][from_col] = None
                return
        else:
            self.en_passant_target = None
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Add to move history
        self.move_history.append((from_pos, to_pos, piece))
    
    def switch_player(self):
        """Switch the current player"""
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.info_label.config(text=f"Current Player: {self.current_player.title()}")
    
    def is_in_check(self, color):
        """Check if a player's king is in check"""
        return self.is_position_in_check(self.board, self.find_king(color), color)
    
    def find_king(self, color):
        """Find the position of a player's king"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece == (color, 'king'):
                    return (row, col)
        return None
    
    def is_position_in_check(self, board, king_pos, color):
        """Check if a position is under attack"""
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece[0] == opponent_color:
                    if self.can_attack_position(board, (row, col), king_pos):
                        return True
        return False
    
    def can_attack_position(self, board, from_pos, target_pos):
        """Check if a piece can attack a specific position"""
        from_row, from_col = from_pos
        target_row, target_col = target_pos
        piece = board[from_row][from_col]
        
        if not piece:
            return False
        
        color, piece_type = piece
        
        # Check piece-specific attack patterns
        if piece_type == 'pawn':
            direction = -1 if color == 'white' else 1
            if (target_row == from_row + direction and 
                abs(target_col - from_col) == 1):
                return True
        elif piece_type == 'rook':
            if (from_row == target_row or from_col == target_col):
                return self.is_path_clear_for_board(board, from_pos, target_pos)
        elif piece_type == 'bishop':
            if abs(from_row - target_row) == abs(from_col - target_col):
                return self.is_path_clear_for_board(board, from_pos, target_pos)
        elif piece_type == 'queen':
            if (from_row == target_row or from_col == target_col or 
                abs(from_row - target_row) == abs(from_col - target_col)):
                return self.is_path_clear_for_board(board, from_pos, target_pos)
        elif piece_type == 'king':
            if (abs(from_row - target_row) <= 1 and abs(from_col - target_col) <= 1):
                return True
        elif piece_type == 'knight':
            row_diff = abs(from_row - target_row)
            col_diff = abs(from_col - target_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True
        
        return False
    
    def is_path_clear_for_board(self, board, from_pos, to_pos):
        """Check if path is clear for a specific board state"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row, current_col = from_row + row_step, from_col + col_step
        
        while (current_row, current_col) != (to_row, to_col):
            if board[current_row][current_col]:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def would_be_in_check_after_move(self, from_pos, to_pos, color):
        """Check if a move would leave the king in check"""
        # Create a copy of the board and make the move
        temp_board = copy.deepcopy(self.board)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        temp_board[to_row][to_col] = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = None
        
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = temp_board[row][col]
                if piece and piece == (color, 'king'):
                    king_pos = (row, col)
                    break
        
        return self.is_position_in_check(temp_board, king_pos, color)
    
    def get_all_valid_moves(self, color):
        """Get all valid moves for a player"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == color:
                    for target_row in range(8):
                        for target_col in range(8):
                            if self.is_valid_move((row, col), (target_row, target_col)):
                                moves.append(((row, col), (target_row, target_col)))
        return moves
    
    def is_checkmate(self, color):
        """Check if a player is in checkmate"""
        if not self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0
    
    def is_stalemate(self, color):
        """Check if a player is in stalemate"""
        if self.is_in_check(color):
            return False
        return len(self.get_all_valid_moves(color)) == 0
    
    def check_game_state(self):
        """Check if the game has ended"""
        if self.is_checkmate(self.current_player):
            winner = 'Black' if self.current_player == 'white' else 'White'
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
            self.game_over = True
        elif self.is_stalemate(self.current_player):
            messagebox.showinfo("Game Over", "Stalemate! It's a draw!")
            self.game_over = True
        elif self.is_in_check(self.current_player):
            self.info_label.config(text=f"Current Player: {self.current_player.title()} - CHECK!")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = self.create_initial_board()
        self.current_player = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.game_over = False
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.en_passant_target = None
        self.move_history = []
        self.info_label.config(text=f"Current Player: {self.current_player.title()}")
        self.update_board_display()
    
    def run(self):
        """Start the game"""
        self.root.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run() 