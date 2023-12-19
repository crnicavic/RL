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
    TOTAL = 4


MOVES = [[0, -1], [0, 1], [-1, 0], [1, 0]]
REWARDS = [-1, -10, None, -1, -1]

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
            self.row += 1 if self.col == (len(board) - 1) else 0 
            self.col = self.col + 1 if self.col+1 < len(board[self.row]) else 0 
            

    def __hash__(self):
        return hash(astuple(self))


TELEPORTS = {}
def create_board(size: tuple[int,int], p: list[float]):

    def create_teleport(tup: tuple[tuple[int,int], cell_type]):
        global TELEPORTS
        (row, col), t = tup
        if t  != cell_type.Teleport:
            return
        pos = position(row, col)
        
        new_row, new_col = np.random.randint(0, len(board), size=2)
        #passing board prevents the coordiantes being a wall, really hacky
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

            new_row, new_col = np.random.randint(0, len(board), size=2)
            del TELEPORTS[pos]
            TELEPORTS.update({pos: position(new_row, new_col, board)})
            break


    board = np.random.choice(range(cell_type.Total.value),size,p=p)
    #No real reason for this, but makes things alot easier
    board[0][0] = cell_type.Regular
    ts = list(map(create_teleport, list(np.ndenumerate(board)))) 
    return board

"""
How range check works:
    * valid indices of my board go from 0 to len(board) - 1
        + if the dimensions of the board are n*n where n is even(i.e 8)
          the last valid index will be an odd number(7)
        + instead of checking if the number is both >= 0 and <= 7
          subtract 7/2 = 3.5 from the index, and if the numbers
          absolute value is less or equal to 3.5, it's good
        + if n is odd, let's say 9, valid indices go from 0 to 8
          this check is simpler
"""
def move(pos: position, dir: direction, board):
    def inrange(x, hi):
        return abs(x - (hi - 1)/2) < hi/2

    new_pos = position(pos.row, pos.col)
    #if new pos is a valid position return it, otherwise old pos stays
    f = lambda s, i: s+i if inrange(s+i, len(board)) else s
    new_pos.row = f(new_pos.row, MOVES[dir][0])
    new_pos.col = f(new_pos.col, MOVES[dir][1])
    #wall collision
    if board[new_pos.row][new_pos.col] == cell_type.Wall:
        return -1
    elif board[new_pos.row][new_pos.col] == cell_type.Teleport:
        while board[new_pos.row][new_pos.col] == cell_type.Teleport:
            new_pos = TELEPORTS[new_pos]

    #this is uglier but actually works
    pos.row, pos.col = new_pos.row, new_pos.col
    return REWARDS[board[pos.row][pos.col]]

    
def init_state_values(board):

    def state_value(state: int):
        return -10*np.random.rand()-1
    
    v = [[state_value(board[row][col]) for col in range(len(board[row]))] \
            for row in range(len(board))]
    return v

GAMMA = 1
def update_state_values(board, v):
    def update_value(row, col, board):
        pv = []
        if board[row][col] >= cell_type.Wall:
            return -np.inf if board[row][col] == cell_type.Wall else 0
        elif board[row][col] == cell_type.Teleport:
            pos = position(row, col)
            tpos = TELEPORTS[pos]
            return v[tpos.row][tpos.col]
        for a in range(direction.TOTAL):
            pos = position(row, col)
            r = move(pos, a, board)
            pv.append(r + GAMMA*v[pos.row][pos.col])
        return max(pv)
    #using map doesn't work with matrices
    v = [[update_value(row, col, board) for col in range(len(board[row]))] \
           for row in range(len(board))]
    return v

TAB_NAMES = ['Board', 'State values']


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
        v_text = [[str(f"{v[row][col]:.2f}") for col in range(len(board[row]))]
                     for row in range(len(board))]
        #python3 is lazy, forcing this to run
        b = list(map(draw_value, repeat(ax), list(np.ndenumerate(v_text))))
    
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
print(TELEPORTS)
pos = position(0, 0, board)
root, tabControl, tabs = init_gui("maze-solver")
canvases, figures, axes = fig_create(tabs)
draw_board(board, axes[0], pos = pos)
v = init_state_values(board)
for i in range(10):
    v = update_state_values(board, v)
print(v)
draw_board(board, axes[1], vals = v) 
for canvas in canvases:
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
tkinter.mainloop()

