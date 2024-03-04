"""reject OOP, embrace monke"""
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

    def __repr__(self):
        return self.name 

    def __str__(self):
        return self.name


MOVES = [[0, -1], [0, 1], [-1, 0], [1, 0]]
REWARDS = [-1, -10, None, -1, -1]

Board = list[list[int]]
Tile = tuple[tuple[int,int], cell_type]
Policy = list[list[direction]]
Q_matrix = list[list[list[float]]]
S_values = list[list[float]]

@dataclass
class position:
    row: int
    col: int
    def __init__(self, row, col, board = None):
        self.row = row
        self.col = col
        if board is None:
            return
        """initial position is a wall fix"""
        while(board[self.row][self.col] == cell_type.Wall):
            self.row += self.col == (len(board) - 1) if self.row < len(board) else 0 
            self.col = self.col + 1 if self.col+1 < len(board[self.row]) else 0 
            

    def __hash__(self):
        return hash(astuple(self))

TAB_NAMES = ['Board', 'State values', 'V-Policy', 'Action Values', 'Q-policy',
             'V-Policy Iteration', 'Q-Policy Iteration']

def init_gui(name: str):
    """Initialize the GUI"""
    root = tkinter.Tk()
    root.wm_title(str)

    """Create the tabs"""
    tabControl = tkinter.ttk.Notebook(root) 
    tabs = [tkinter.Frame(tabControl) for _ in range(len(TAB_NAMES))]

    for i in range(len(TAB_NAMES)):
        tabControl.add(tabs[i], text=TAB_NAMES[i])

    tabControl.pack(expand = 1, fill ="both") 
    
    button_quit = tkinter.Button(master=root, text="Quit", command=exit)
    button_quit.pack(side=tkinter.BOTTOM)
    return root, tabControl, tabs


def fig_create \
(tabs):
    """Create the Figures and Draw them to a canvas"""
    figures = []
    """multiple of axis is axes, storing all axises? configurations"""
    axes = [] 

    rows, cols = 1, 1
    for i in range(len(TAB_NAMES)):
        fig, ax = plt.subplots(rows, cols)
        figures.append(fig)
        axes.append(ax)

    """Created figures are "connected" to a window canvas"""
    canvases = [FigureCanvasTkAgg(figures[i], master=tabs[i]) \
    for i in range(len(TAB_NAMES))]

    return canvases, figures, axes


TELEPORTS = {}
def create_board \
(size: tuple[int,int], p: list[float]) -> Board:

    def create_teleport(tup: Tile):
        global TELEPORTS
        (row, col), t = tup
        if t  != cell_type.Teleport:
            return
        pos = position(row, col)
        
        new_row, new_col = np.random.randint(0, len(board), size=2)
        """passing board prevents the coordiantes being a wall, hacky"""
        TELEPORTS[pos] = position(new_row, new_col, board)  

        """loop to find cyclic teleports"""
        next_pos = pos
        while board[next_pos.row][next_pos.col] == cell_type.Teleport:
            """follow the teleport"""
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
    """No real reason for this, but makes things alot easier"""
    board[0][0] = cell_type.Regular
    ts = list(map(create_teleport, list(np.ndenumerate(board)))) 
    return board


def draw_board \
(board: Board, ax, pos: position = None, vals = None):

    """"help" function """
    def draw_value(ax, tup: tuple[tuple[int, int], str]):
        (row, col), val = tup
        ax.text(col-0.2, row, val)

    color_grid = [[COLORS[board[row][col]] for col in range(len(board[row]))] \
                    for row in range(len(board))]
    ax.imshow(color_grid)
    for (row, col), t in list(np.ndenumerate(board)):
        if t != cell_type.Teleport:
            continue
        tp = position(row, col)
        dest = TELEPORTS[tp]
        dx, dy = dest.col - tp.col, dest.row - tp.row 
        ax.arrow(x=tp.col, y=tp.row, dx=dx, dy=dy, width=0.05, color='purple')
    if vals is not None:
        strf = lambda n: str(n) if not isinstance(n, float) else f"{n:.2f}"
        v_text = [[strf(vals[row][col]) for col in range(len(board[row]))] \
                     for row in range(len(board))]
        """python3 is lazy, forcing this to run"""
        b = list(map(draw_value, repeat(ax), list(np.ndenumerate(v_text))))
    
    if pos is not None:
        ax.text(pos.col, pos.row, "X")


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
def move \
(pos: position, dir: direction, board: list[list[int]]) -> int:
    def inrange(x, hi):
        return abs(x - (hi - 1)/2) < hi/2

    new_pos = position(pos.row, pos.col)
    """if new pos is a valid position return it, otherwise old pos stays"""
    f = lambda s, i: s+i if inrange(s+i, len(board)) else s
    new_pos.row = f(new_pos.row, MOVES[dir][0])
    new_pos.col = f(new_pos.col, MOVES[dir][1])
    """wall collision"""
    if board[new_pos.row][new_pos.col] == cell_type.Wall:
        return -np.inf
    elif board[new_pos.row][new_pos.col] == cell_type.Teleport:
        while board[new_pos.row][new_pos.col] == cell_type.Teleport:
            new_pos = TELEPORTS[new_pos]

    """if the position didn't change the agent tried going out of bounds""" 
    if new_pos == pos:
        return -np.inf

    """this is uglier but actually works"""
    pos.row, pos.col = new_pos.row, new_pos.col
    return REWARDS[board[pos.row][pos.col]]

    
def value_iteration \
(board: Board, eps=0.01, gamma= 1, maxiter=100) -> (list[list[float]], Policy):

    def random_state_value():
        return -10*np.random.rand()-1
    
    def random_action():
        return np.random.randint(0, direction.TOTAL)

    """
    bellman for v values
        * if the field it's being calculated for
        is terminal v=0
        * if the field is a wall it's -inf because
        it isn't steppable
        * if it's a teleport i assigned it the value of
        the destination field
    """
    def update_value(row, col, board, v):
        if board[row][col] >= cell_type.Wall:
            val = -np.inf if board[row][col] == cell_type.Wall else 0
            return val, None
        elif board[row][col] == cell_type.Teleport:
            pos = position(row, col)
            pos = TELEPORTS[pos]
            return v[pos.row][pos.col], None

        pv = []
        for a in range(direction.TOTAL):
            pos = position(row, col)
            r = move(pos, a, board)
            pv.append(r + gamma*v[pos.row][pos.col])
        maxind = np.argmax(pv)
        return (pv[maxind], direction(maxind))

    """calling that calculates bellman for every field to reduce indentation"""
    def update_state_values(board, v, s, gamma = 1):
        """using map doesn't work with matrices"""
        for (row, col), _ in list(np.ndenumerate(board)):
            v[row][col], s[row][col] = update_value(row, col, board, v)
        return v, s

    """this is easier to implement but works"""
    def vmean(v):
        total = 0
        count = 0
        for (row, col), val in list(np.ndenumerate(v)):
            if v[row][col] == -np.inf:
                continue
            count += 1
            total += val
        return total/count
    
    """initial state values and actions are random"""
    v = [[-10*np.random.rand()-1 for col in range(len(board[row]))] \
            for row in range(len(board))]
    
    s = [[direction(random_action()) for col in range(len(board[row]))] \
            for row in range(len(board))]

    old_mean = vmean(v)
    new_mean = old_mean
    for it in range(maxiter):
        v, s = update_state_values(board, v, s, gamma)
        new_mean = vmean(v)
        if abs(new_mean - old_mean) < eps:
            print(f"V-Iteration Converged after {it} iterations")
            break
        old_mean = new_mean

    return v,s


def action_value_iteration \
(board: Board, eps=0.01, gamma=1, maxiter=100) -> (Q_matrix, Policy, S_values): 
    """
    * if the field it's being calculated for
    is terminal q=0
    * if the field is a wall it's -inf because
    it isn't steppable
    * if it's a teleport i assigned it the value of
    the destination field
    of course these values are set for each action
    """
    def update_value(row, col, board, q, gamma=1):
        if board[row][col] >= cell_type.Wall:
            val = -np.inf if board[row][col] == cell_type.Wall else 0
            return [val] * 4
        elif board[row][col] == cell_type.Teleport:
           pos = position(row, col)
           tpos = TELEPORTS[pos]
           return q[tpos.row][tpos.col] 
    
        val = [0] * 4
        for a in range(direction.TOTAL):
           pos = position(row, col)
           r = move(pos, a, board) 
           val[a] = r + gamma * max(q[pos.row][pos.col])

        return val 

    def update_q(board, q, gamma = 1):
        for (row, col), _ in list(np.ndenumerate(board)):
            q[row][col] = update_value(row, col, board, q)
        return q

    def qmean(q, board):
        total = 0
        count = 0
        for (row, col), _ in list(np.ndenumerate(board)):
            if -np.inf in q[row][col]:
                continue
            count += 1
            total += np.mean(q[row][col])
        return total/count


    q = [[[-10*np.random.rand()-1 for a in range(direction.TOTAL)] \
            for col in range(len(board[row]))] for row in range(len(board))]

    old_mean = qmean(q, board)
    new_mean = old_mean
    for it in range(maxiter):
        q = update_q(board, q, gamma)
        new_mean = qmean(q, board)
        if abs(new_mean - old_mean) < eps:
            print(f"Q-Iteration Converged after {it} iterations")
            break
        old_mean = new_mean

    """used for plotting"""
    a = [[direction(0) for col in range(len(board[row]))] \
            for row in range(len(board))]
    vals = [[0 for col in range(len(board[row]))] \
            for row in range(len(board))]
    for (row, col), t in list(np.ndenumerate(board)):
        """best action for each state"""
        a[row][col] = direction(np.argmax(q[row][col]))
        """the value of that action"""
        vals[row][col] = q[row][col][a[row][col]]
        if t >= cell_type.Teleport:
            a[row][col] = None
    return q, a, vals


def v_policy_iteration \
(board: Board, gamma:float=1) -> Policy:

    """not sure how to name this, state value for applied action"""
    def state_value(row, col, t, a, v, gamma=1):
        pv = []
        if t >= cell_type.Wall:
            return -np.inf if t == cell_type.Wall else 0
        elif board[row][col] == cell_type.Teleport:
            pos = position(row, col)
            pos = TELEPORTS[pos]
            return v[pos.row][pos.col]
        pos = position(row, col)
        r = move(pos, a, board)
        return r + gamma * v[pos.row][pos.col]
            

    def evaluate_pi(board, pi, v, gamma=1):
        for (row, col), t in list(np.ndenumerate(board)):
            v[row][col] = state_value(row, col, t, pi[row][col], v, gamma)
        return v

    """take state values and calculate a greedy policy"""
    def greedy_policy(board, v, gamma=1):
        new_pi = [[0 for col in range(len(board[row]))] \
                for row in range(len(board))]
        for (row, col), t in np.ndenumerate(board):
            pv = [state_value(row, col, t, a, v, gamma) \
                    for a in range(direction.TOTAL)]
            new_pi[row][col] = direction(np.argmax(pv))
        return new_pi
            

    v = [[-10*np.random.rand()-1 for col in range(len(board[row]))] \
            for row in range(len(board))]
    pi = greedy_policy(board, v, gamma)

    """emulating a do while loop"""
    it = 0
    while True:
        v = evaluate_pi(board, pi, v, gamma)
        new_pi = greedy_policy(board, v, gamma)
        if pi == new_pi:
            break
        pi = new_pi
        it+=1
    print(f"V-Policy Iteration converged after {it} iterations")
    return pi

def q_policy_iteration \
(board: Board, gamma: float=1) -> Policy:

    def action_value(row, col, board, a, q, pi, gamma=1):
        if board[row][col] >= cell_type.Wall:
            val = -np.inf if board[row][col] == cell_type.Wall else 0
            return val 
        elif board[row][col] == cell_type.Teleport:
           pos = position(row, col)
           tpos = TELEPORTS[pos]
           return q[tpos.row][tpos.col][pi[tpos.row][tpos.col]] 
        pos = position(row, col)
        r = move(pos, a, board) 
        return r + gamma * q[pos.row][pos.col][pi[pos.row][pos.col]]

    def evaluate_all(board, pi, q, gamma=1):
        for (row, col), t in np.ndenumerate(board):
            q[row][col] = [ action_value(row, col, board, a, q, pi, gamma) \
                    for a in range(direction.TOTAL)]
        return q

    #if i want to strictly adhere to pseudocode
    def evaluate_pi(board, pi, q, gamma=1):
        for (row, col), a in np.ndenumerate(pi):
            q[row][col][a] = action_value(row, col, board, a, q, pi, gamma)
        return q
    
    def greedy_policy(board, q, gamma=1):
        new_pi = [[0 for col in range(len(board[row]))] \
                for row in range(len(board))]
        for (row, col), t in np.ndenumerate(board):
            new_pi[row][col] = direction(np.argmax(q[row][col]))
        return new_pi

    q = [[[-10*np.random.rand()-1 for a in range(direction.TOTAL)] \
            for col in range(len(board[row]))] for row in range(len(board))]
    pi = greedy_policy(board, q, gamma)
    it = 0
    while it < 1000:
        q = evaluate_all(board, pi, q, gamma)
        new_pi = greedy_policy(board, q, gamma)
        if pi == new_pi:
            break
        pi = new_pi
        it += 1
    print(f"Q-Policy Iteration converged after {it} iterations")
    return pi

board = create_board((8, 8), [0.6, 0.1, 0.05, 0.2, 0.05])
pos = position(0, 0, board)
root, tabControl, tabs = init_gui("maze-solver")
canvases, figures, axes = fig_create(tabs)
draw_board(board, axes[0], pos = pos)
v, s = value_iteration(board)
q, a, av = action_value_iteration(board)
pi_v = v_policy_iteration(board)
pi_q = q_policy_iteration(board)
draw_board(board, axes[1], vals = v) 
draw_board(board, axes[2], vals = s)
draw_board(board, axes[3], vals = av)
draw_board(board, axes[4], vals = a)
draw_board(board, axes[5], vals = pi_v)
draw_board(board, axes[6], vals = pi_q)
for canvas in canvases:
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
tkinter.mainloop()

