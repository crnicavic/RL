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

from dataclasses import dataclass

@dataclass
class Bandit:
    mean: float
    span: int

#pulling a lever returns a number in range (mean-span, mean+span)
def pull(index: int, bandits: list[Bandit]):
    if index >= len(bandits):
        return -1000
    mean, span = bandits[index].mean, bandits[index].span
    return mean + span * 2 *(np.random.rand() - 0.5)

#everytime this pull function is called, the mean changes for up to 15%
def chaos_pull(index: int, bandits: list[Bandit]):
    if index >= len(bandits):
        return -1000
    #Pull the lever -> get a reward -> the mean changes
    #commented because right now I wish to this differently
    mean, span = bandits[index].mean, bandits[index].span
    return mean + span * 2 *(rand.rand() - 0.5)


#it's just a joke, but probably the most realistic
def complete_chaos_pull(index: int, bandits: list[Bandit]):
    if index >= len(bandits):
        return -1000
    mean, span = bandits[index].mean, bandits[index].span
    if rand.rand() < 0.1e-10:
        raise Exception("haha")
    bandits[index].mean *= rand.rand() * 0.5 + 0.5
    bandits[index].span *= rand.rand() * 0.5 + 0.5
    if bandits[index].mean > 200:
        raise Exception("Too Good, sorry")
    if bandits[index].span < 0.1:
        raise Exception("Too consistent, sorry")
    bandits = rand.shuffle(bandits)
    return mean + span * 2 *(rand.rand() - 0.5)


def train(bandits: list[Bandit], EPS, ITERS = 5000):
    q = [100 for _ in range(BANDIT_COUNT)]
    #each column of the training log is one iteration of q's
    training_log = np.zeros((BANDIT_COUNT, ITERS))
    rewards = np.zeros(ITERS)

    for i in range(ITERS):
        a = np.argmax(q) if rand.rand() > EPS else rand.randint(0,BANDIT_COUNT)
        #stored like this for later plotting
        rewards[i] = pull(a, bandits)
        q[a] = q[a] + ALPHA * (rewards[i] - q[a])
        # i hate this, can't figure out how to transpose stuff
        for j in range(len(q)):
            training_log[j][i] = q[j]
    return q, rewards, training_log


#writing a new function isn't elegant, but probably simpler
def chaos_train(bandits: list[list[Bandit]], pullf: callable, EPS, ITERS = 5000):
    q = [100 for _ in range(BANDIT_COUNT)]
    #each column of the training log is one iteration of q's
    rewards = np.zeros(ITERS)
    ideal_rewards = np.zeros(ITERS)

    for i in range(ITERS):
        a = np.argmax(q) if rand.rand() > EPS else rand.randint(0,BANDIT_COUNT)
        #stored like this for later plotting
        rewards[i] = pullf(a, bandits[i])
        q[a] = q[a] + ALPHA * (rewards[i] - q[a])
        ideal_rewards[i] = max(b.mean for b in bandits[i])
    return q, rewards, np.cumsum(ideal_rewards)


def test(bandits: list[Bandit], q: list[float], ITERS = 1000):
    rewards = np.zeros(ITERS)
    for i in range(ITERS):
        a = np.argmax(q)
        rewards[i] = pull(a, bandits)
    
    return rewards


def chaos_test(bandits: list[list[Bandit]], q: list[float], pullf: callable, ITERS = 1000):
    rewards = np.zeros(ITERS)
    ideal_rewards = np.zeros(ITERS)
    for i in range(ITERS):
        a = np.argmax(q)
        rewards[i] = pullf(a, bandits[i])
        ideal_rewards[i] = max([b.mean for b in bandits[i]])
    
    return rewards, np.cumsum(ideal_rewards)


#slider callback function to plot the q change over time for different eps
def switch_eps_plot(eps_index: int):
    log = training_logs[int(eps_index)-1]
    figures[2].suptitle(f"eps={EPSILONS[int(eps_index)-1]}")
    for i in range(BANDIT_COUNT):
        row, col = i // len(axes[2][0]), i % len(axes[2][0])
        axes[2][row][col].clear()
        #ommiting the first 100 values just to showcase the convergence better
        axes[2][row][col].plot(log[row*len(axes[2][row]) + col][100:])
        axes[2][row][col].plot(bandits[i].mean*np.ones(len(log[0]) - 100)) 
    print(tabControl.index("current"))
    canvases[2].draw()


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
    
    button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)
    button_quit.pack(side=tkinter.BOTTOM)
    slider = tkinter.Scale(tabs[2], 
                            from_=1, to=len(EPSILONS), 
                            orient=tkinter.HORIZONTAL, 
                            command=switch_eps_plot)
    slider.pack(side=tkinter.BOTTOM)
    return root, tabControl, tabs


def fig_create(tabs):
    #Create the Figures and Draw them to a canvas
    figures = []
    #multiple of axis is axes, storing all axises? configurations
    axes = [] 
    figure_sizes = [(len(EPSILONS), 1), (2, (BANDIT_COUNT + 1)//2)]

    #create figures and axes whre the plots will be drawn
    for i in range(len(TAB_NAMES)):
        #only the third tab has a different subplot grid
        rows, cols = figure_sizes[0] if i != 2 else figure_sizes[1] 
        fig, ax = plt.subplots(rows, cols)
        figures.append(fig)
        axes.append(ax)

    #Created figures are "connected" to a window canvas
    canvases = [FigureCanvasTkAgg(figures[i], master=tabs[i]) \
    for i in range(len(TAB_NAMES))]
    
    toolbar = NavigationToolbar2Tk(canvases[0], root, pack_toolbar=False)
    toolbar.update()

    return canvases, figures, axes

#globals because I don't know how to make the GUI work otherwise
TAB_NAMES = ['1) Training', '2)Test', '3)Q Convergence', '4)Chaos Training', '5)Chaos Test']
BANDIT_COUNT = 5
TRAINING_ITERS = 5000
ALPHA = 0.1
# lower epsilon -> random action is less frequent
EPSILONS = [0.5, 0.1, 0.001, 0]
TESTING_ITERS = 300

root, tabControl, tabs = init_gui("MultiArm Bandit")
canvases, figures, axes = fig_create(tabs) 

bandits = [Bandit((np.random.rand() - 0.5) * 10, np.random.rand() * 10) \
for _ in range(BANDIT_COUNT)] 

best_bandit = max([b.mean for b in bandits])

ideal_gain = np.cumsum(best_bandit * np.ones(TRAINING_ITERS-1))
#pretty pointless, calculates where to write the annotation
anot = (10, ideal_gain[-1]-1000)
#when i start testing i will save the learnt q's 
testing_q = []
training_logs = []

for row in range(len(EPSILONS)):
    q, rewards, t = train(bandits,  EPSILONS[row])
    training_logs.append(t)
    
    axes[0][row].plot(np.cumsum(rewards))
    axes[0][row].plot(ideal_gain)
    axes[0][row].annotate(f"for EPSILON={EPSILONS[row]}", xy=(anot))
    
    testing_q.append(q)


#setting up for testing - not optimal, but for the sake of readability
ideal_gain = np.cumsum(best_bandit * np.ones(TESTING_ITERS-1))
anot = (10, ideal_gain[-1] * 0.9)

for row in range(len(EPSILONS)):
    rewards = test(bandits, testing_q[row], TESTING_ITERS)

    axes[1][row].plot(np.cumsum(rewards))
    axes[1][row].plot(ideal_gain)
    axes[1][row].annotate(f"for EPSILON={EPSILONS[row]}", xy=(anot))

#draw the first thing
switch_eps_plot(1)


"""
now the fun part, the means change
generating the means for every bandit for every iteration ahead of time
just to see how the different Epsilons stack against each other
"""
#function to change the mean of a bandit
def change_mean(b):
    return Bandit(b.mean * (rand.rand() * 0.3) + 0.85, b.span)


#function to generate how the bandits change over time
def embrace_chaos(PULL_COUNT: int, init_value: list[Bandit]):
    bandits = []
    bandits.append(init_value) 
    for i in range(PULL_COUNT-1):
        bandits.append(list(map(change_mean, bandits[i-1])))
    return bandits
        
chaos_bandits = embrace_chaos(TRAINING_ITERS, bandits)
for row in range(len(EPSILONS)):
    q, rewards, ideal_gain = chaos_train(chaos_bandits, chaos_pull, EPSILONS[row])
    
    axes[3][row].plot(np.cumsum(rewards))
    axes[3][row].plot(ideal_gain)
    axes[3][row].annotate(f"for EPSILON={EPSILONS[row]}", xy=(anot))
    
    testing_q.append(q)

#and finally, see how we compare in the real world
chaos_bandits = embrace_chaos(TESTING_ITERS, chaos_bandits[-1])
for row in range(len(EPSILONS)):
    rewards, ideal_gain = chaos_test(chaos_bandits, testing_q[row], chaos_pull, TESTING_ITERS)

    axes[4][row].plot(np.cumsum(rewards))
    axes[4][row].plot(ideal_gain)
    axes[4][row].annotate(f"for EPSILON={EPSILONS[row]}", xy=(anot))

for canvas in canvases:
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
