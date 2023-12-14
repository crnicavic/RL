#reject OOP, embrace monke
from numpy import random as rand
import matplotlib.pyplot as plt

import tkinter
from tkinter import ttk

import numpy as np

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

from dataclasses import dataclass, astuple

from enum import IntFlag

from itertools import repeat

class cell_type(IntFlag):
    Regular = 0,
    Penalty = 1,
    Teleport = 2,
    Wall = 3,
    Terminal = 4,
    Total = 5

REWARDS = [-1, -10, None, 0, 0]
COLORS = [(0xFF, 0xFF, 0xFF),   #Regular = white
          (0xFF, 0x00, 0x00),   #Penalty = red
          (0x00, 0xFF, 0x00),   #Teleport = green
          (0x00, 0x00, 0x00),   #Wall = black
          (0x00, 0x00, 0xFF)]   #Terminal = blue

class direction(IntFlag):
    LEFT = 0,
    RIGHT = 1,
    UP = 2, 
    DOWN  = 3


MOVES = [[0, -1], [0, 1], [-1, 0], [1, 0]]

@dataclass
class position:
    row: int
    col: int
    def __init__(self, row, col, board = None):
        self.row = row
        self.col = col
        if board is None:
            return
        #initial position is a wall fix
        while(board[self.row][self.col] == cell_type.Wall):
            self.row += 1 if self.col >= len(board) else 0 
            self.col = self.col + 1 if self.col < len(board[self.row]) else 0 
            

    def __hash__(self):
        return hash(astuple(self))


def move(pos: position, dir: direction):
    new_pos = position(pos.row + MOVES[dir][0], pos.col + MOVES[dir][1]) 
    #wall collision
    if board[new_pos.row][new_pos.col] == cell_type.Wall:
        return -1
    elif board[new_pos.row][new_pos.col] == cell_type.Teleport:
        pos = position(TELEPORTS(pos))
    #optimized range check
    pos.row += MOVES[dir][0] if abs(pos.row - (len(board)-1)/2) < 4 else 0 
    pos.col += MOVES[dir][1] if abs(pos.col - (len(board)-1)/2) < 4 else 0
    

TELEPORTS = {}
def create_board(size: tuple[int,int], p: list[float]):

    def create_teleport(tup: tuple[tuple[int,int], cell_type]):
        global TELEPORTS
        (row, col), t = tup
        if t  != cell_type.Teleport:
            return
        pos = position(row, col)
        
        new_row, new_col = np.random.randint(0, len(board), size=2)
        TELEPORTS[pos] = position(new_row, new_col, board)  

        #loop to find cyclic teleports
        next_pos = pos
        #way too much indentation
        while board[next_pos.row][next_pos.col] == cell_type.Teleport:
            #follow the teleport
            next_pos = TELEPORTS[next_pos]

            if next_pos not in TELEPORTS:
                break
            elif next_pos != pos:
                continue

            print("ERROR: CIRCULAR TELEPORTS")
            new_row, new_col = np.random.randint(0, len(board), size=2)
            del TELEPORTS[pos]
            TELEPORTS.update({pos: position(new_row, new_col, board)})
            break


    board = np.random.choice(range(cell_type.Total.value),size,p=p)
    ts = list(map(create_teleport, list(np.ndenumerate(board)))) 
    return board


def init_state_values(board):

    def state_value(state: int):
        if state <= cell_type.Wall:
            return -10*np.random.rand()
        elif state == cell_type.Wall:
            return -np.ifn
        return 0

    v = [[state_value(board[row][col]) for col in range(len(board[row]))] \
            for row in range(len(board))]
    return v


TAB_NAMES = ['Board', 'state_values']


def init_gui(name: str):
    #Initialize the GUI
    root = tkinter.Tk()
    root.wm_title(str)

    #Create the tabs
    tabControl = tkinter.ttk.Notebook(root) 
    tabs = [tkinter.Frame(tabControl) for _ in range(len(TAB_NAMES))]

    for i in range(len(TAB_NAMES)):
        tabControl.add(tabs[i], text=TAB_NAMES[i])

    tabControl.pack(expand = 1, fill ="both") 
    
    button_quit = tkinter.Button(master=root, text="Quit", command=exit)
    button_quit.pack(side=tkinter.BOTTOM)
    return root, tabControl, tabs


def draw_board(board, ax, pos = None, vals = None):

    #"help" function 
    def draw_value(ax, tup: tuple[tuple[int, int], str]):
        (row, col), val = tup
        ax.text(col-0.2, row, val)

    color_grid = [[COLORS[board[row][col]] for col in range(len(board[row]))]
                    for row in range(len(board))]
    ax.imshow(color_grid)
    if vals is not None:
        vals_text = [[str(f"{v[row][col]:.2f}") for col in range(len(board[row]))]
                     for row in range(len(board))]
        #python3 is lazy, forcing this to run
        b = list(map(draw_value, repeat(ax), list(np.ndenumerate(vals_text))))
    
    if pos is not None:
        ax.text(pos.col, pos.row, "X")


def fig_create(tabs):
    #Create the Figures and Draw them to a canvas
    figures = []
    #multiple of axis is axes, storing all axises? configurations
    axes = [] 

    rows, cols = 1, 1
    for i in range(len(TAB_NAMES)):
        fig, ax = plt.subplots(rows, cols)
        figures.append(fig)
        axes.append(ax)

    #Created figures are "connected" to a window canvas
    canvases = [FigureCanvasTkAgg(figures[i], master=tabs[i]) \
    for i in range(len(TAB_NAMES))]

    return canvases, figures, axes

board = create_board((8, 8), [0.7, 0.1, 0.1, 0.05, 0.05])

pos = position(0, 0, board)
root, tabControl, tabs = init_gui("maze-solver")
canvases, figures, axes = fig_create(tabs)
v = init_state_values(board)
draw_board(board, axes[0], pos = pos)
draw_board(board, axes[1], vals = v) 
for canvas in canvases:
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
tkinter.mainloop()

