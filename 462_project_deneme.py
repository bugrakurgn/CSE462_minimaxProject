#Bugra Kurgan 20210702025
import tkinter as tk
from tkinter import messagebox, simpledialog
from my_agent import minimax, dynamic_depth

ROWS, COLS = 7, 7
CELL_SIZE = 80
MAX_DEPTH = 5
AI_COLOR = "red"
HUMAN_COLOR = "blue"
EMPTY_COLOR = "white"

def initialize_board():
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    # AI pieces (triangles)
    board[0][0], board[4][6] = 1, 1
    board[2][0], board[6][6] = 1, 1
    # Human pieces (circles)
    board[0][6], board[4][0] = 2, 2
    board[6][0], board[2][6] = 2, 2
    return board

def draw_board(canvas, board):
    canvas.delete("all")
    for i in range(ROWS):
        for j in range(COLS):
            x0, y0 = j * CELL_SIZE, i * CELL_SIZE
            x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
            canvas.create_rectangle(x0, y0, x1, y1, fill=EMPTY_COLOR, outline="black")
            if board[i][j] == 1:  # triangle
                canvas.create_polygon(
                    x0 + CELL_SIZE // 2, y0 + 10, 
                    x0 + 10, y1 - 10,
                    x1 - 10, y1 - 10,
                    fill=AI_COLOR
                )
            elif board[i][j] == 2:  # circle
                canvas.create_oval(
                    x0 + 10, y0 + 10, x1 - 10, y1 - 10, fill=HUMAN_COLOR
                )

def show_info():
    messagebox.showinfo(
        "Game Info",
        "Rules of the Game:\n\n"
        "1. The AI pieces are red triangles, and the Human pieces are blue circles.\n"
        "2. The goal is to capture all opponent pieces by surrounding them vertically or horizontally between your pieces or wall.\n"
        "3. The AI and Human take turns one by one.\n"
        "4. Each player can move two different pieces in a single turn.\n"
        "5. The game ends when one player has no pieces left or after 50 moves with the winner of the most pieces on the board.\n\n"
        "IMPORTANT NOTE: FOR AI TO MAKE A MOVE, YOU NEED TO CLICK ON THE BOARD.\n"
        "Depth of the minimax can be changed through my_agent.py dynamic_depth function between lines 45-52\n"
        "Developer: Bugra Kurgan 20210702025"
    )

def create_menu(window):
    menu_bar = tk.Menu(window)
    info_menu = tk.Menu(menu_bar, tearoff=0)
    info_menu.add_command(label="Game Info", command=show_info)
    menu_bar.add_cascade(label="Info", menu=info_menu)
    window.config(menu=menu_bar)

def check_captures():
    global board, captures
    captures = []
    for i in range(ROWS):
        for j in range(COLS):
            if board[i][j] == 0:
                continue

            player = board[i][j]
            opponent = 3 - player
            if j > 0 and j < COLS - 1:
                if board[i][j - 1] == opponent and board[i][j + 1] == opponent:
                    captures.append((i, j))

            if i > 0 and i < ROWS - 1:
                if board[i - 1][j] == opponent and board[i + 1][j] == opponent:
                    captures.append((i, j))

            if j == 0 and board[i][j + 1] == opponent:
                captures.append((i, j))
            elif j == COLS - 1 and board[i][j - 1] == opponent:
                captures.append((i, j))
            if i == 0 and board[i + 1][j] == opponent:
                captures.append((i, j))
            elif i == ROWS - 1 and board[i - 1][j] == opponent:
                captures.append((i, j))

def apply_captures():
    global board, captures
    for i, j in captures:
        if board[i][j] != 0:  
            board[i][j] = 0
    draw_board(canvas, board)

def check_game_end():
    global board

    ai_pieces = sum(row.count(1) for row in board)
    human_pieces = sum(row.count(2) for row in board)

    if ai_pieces == 0:
        end_game("Human wins! All AI pieces captured.")
    elif human_pieces == 0:
        end_game("AI wins! All Human pieces captured.")

    if ai_pieces > 0 and human_pieces == 0:
        end_game("AI wins! Human has no pieces left.")
        return
    elif human_pieces > 0 and ai_pieces == 0:
        end_game("Human wins! AI has no pieces left.")
        return

    if move_count >= 50:
        if ai_pieces > human_pieces:
            end_game("AI wins! AI has more pieces after 50 moves.")
        elif human_pieces > ai_pieces:
            end_game("Human wins! Human has more pieces after 50 moves.")
        else:
            end_game("It's a Draw! Both players have the same number of pieces after 50 moves.")
        return

def end_game(message):
    global window
    end_label = tk.Label(window, text=message, font=("Helvetica", 16), fg="red")
    end_label.pack()
    canvas.unbind("<Button-1>")

def ai_move():
    global board
    moved_pieces = set()
    MAX_DEPTH = dynamic_depth(move_count)
    for _ in range(2):
        valid_moves = [
            move for move in get_valid_moves(board, 1)
            if move[0] not in moved_pieces]  

        if not valid_moves:
            break  

        _, best_move = minimax(board, 0, MAX_DEPTH, True, float('-inf'), float('inf'), moved_pieces)

        if best_move:
            start, end = best_move
            move_piece(start, end)
            moved_pieces.add(end) 
            check_captures()
            apply_captures()
            check_game_end()
        else:
            break

def get_valid_moves(board, player):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == player:
                for d_row, d_col in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Directions: right, left, down, up
                    new_row, new_col = i + d_row, j + d_col
                    if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]) and board[new_row][new_col] == 0:
                        moves.append(((i, j), (new_row, new_col)))
    return moves

def on_click(event):
    global selected_piece, current_turn, move_count, moved_pieces

    if current_turn == 1:  # AI's turn
        ai_move()
        current_turn = 2
        update_turn_label()
        check_game_end()
        return

    # Human's turn
    row, col = event.y // CELL_SIZE, event.x // CELL_SIZE

    if selected_piece:
        start_row, start_col = selected_piece
        if move_piece(selected_piece, (row, col)):
            moved_pieces.append((row, col))
            selected_piece = None
            check_captures()
            apply_captures()
            check_game_end()

            move_count += 1
            if move_count >= 2 or get_player_piece_count(current_turn) <= len(moved_pieces):
                current_turn = 3 - current_turn
                move_count = 0
                moved_pieces = []
                update_turn_label()
        else:
            selected_piece = None
    else:
        if board[row][col] == current_turn and (row, col) not in moved_pieces:
            selected_piece = (row, col)

def move_piece(start, end):
    global board
    start_row, start_col = start
    end_row, end_col = end

    if abs(start_row - end_row) + abs(start_col - end_col) == 1:
        if board[start_row][start_col] and board[end_row][end_col] == 0:
            board[end_row][end_col] = board[start_row][start_col]
            board[start_row][start_col] = 0
            draw_board(canvas, board)
            return True
    return False

def get_player_piece_count(player):
    return sum(row.count(player) for row in board)

def update_turn_label():
    if current_turn == 1:
        turn_label.config(text="It's the AI's turn (Triangle)")
    else:
        turn_label.config(text="It's the Human's turn (Circle)")

def choose_starting_player():
    global current_turn
    starting_player = simpledialog.askstring("Choose Starting Player", "Who should start first? (AI or Human):\n\nPlease write ai or human precisely.")
    if starting_player is None or starting_player.lower() not in ["ai", "human"]:
        messagebox.showerror("Invalid Input", "Invalid choice! Defaulting to AI's turn.")
        current_turn = 1  # Default to AI
    else:
        current_turn = 1 if starting_player.lower() == "ai" else 2


board = initialize_board()
selected_piece = None
captures = []
move_count = 0
moved_pieces = []

window = tk.Tk()
window.title("Strategic Board Game")
create_menu(window)

canvas = tk.Canvas(window, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE)
canvas.pack()

turn_label = tk.Label(window, text="", font=("Helvetica", 14))
turn_label.pack()

choose_starting_player()
#select_starting_player1()
update_turn_label()

draw_board(canvas, board)

canvas.bind("<Button-1>", on_click)

window.mainloop()
