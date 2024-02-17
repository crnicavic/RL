"""
reject OOP, embrace monke
"""

import numpy as np


import matplotlib.pyplot as plt

import tkinter
from tkinter import ttk

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
            NavigationToolbar2Tk)
from matplotlib.figure import Figure

from dataclasses import dataclass, astuple

from enum import IntFlag, Enum

import copy

"""
Repeat the functionality of this notebook using more realistic Blackjack rules. 
For example, in the actual game of Blackjack each player immediately gets two cards 
(however, only one of the dealer's cards is known to the player, 
before the player finishes his/hers turn).
"""
class Rank(IntFlag):
    TWO=2
    THREE=3
    FOUR=4
    FIVE=5
    SIX=6
    SEVEN=7
    EIGHT=8
    NINE=9
    TEN=10
    ACE=11 #blackjack hacks
    JACK=12
    QUEEN=13
    KING=14
    RANK_TOTAL=15


class Suit(IntFlag):
    CLUBS=0
    DIAMONDS=1
    HEARTS=2
    SPADES=3
    SUIT_TOTAL=4


@dataclass
class Card:
    value: Rank
    suit: Suit


@dataclass
class State:
    cards: [Card]
    total: int
    optotal: int    #sum visible to the opposite side of the table 

def deck_init(deck_count=1):
    l = lambda r : r if r <= 11 else 10
    deck = [Card(l(rank), suit) for rank in range(Rank.TWO, Rank.RANK_TOTAL) \
            for suit in range(Suit.SUIT_TOTAL) for _ in range(deck_count)]
    np.random.shuffle(deck)
    return deck

#index of current card
topdeck = -1
#position of the cut - realisticly it's about 70
CUT = 20

#rcpt - recipient of the card
def draw(deck, rcpt, count=1):
    global topdeck
    for _ in range(count):
        if len(deck) + topdeck < CUT:
            topdeck = -1
            np.random.shuffle(deck)
        rcpt.cards.append(deck[topdeck])
        rcpt.total += rcpt.cards[-1].value
        topdeck -= 1


def hold(deck, rcpt, count=1):
    return 0
        

#emulating function pointers
ACTIONS = [draw, hold]


def deal(deck):
    dealer = State([], 0, 0)
    draw(deck, dealer, count=2)
    #making it an array incase I want to add spliting
    player = [State([], 0, 0)]
    draw(deck, player[0], count=2)

    return dealer, player

#reduce the value of an ace if the player is about to bust
def ace_reduce(state):
    if state.total <= 21:
        return
    c_id = 0
    while state.total > 21 and c_id < len(state.cards):
        card = state.cards[c_id]
        state.total -= 10 if card.value == 11 else 0 #BLACJACK HAX
        card.value -= 10 if card.value == 11 else 0
        c_id += 1
    return


#HIT = 0, HOLD = 1, simple
def dealer_pi(state: State):
    def ace(state: State):
        ace = [card.value == 11 for card in state.cards]
        return True in ace
    
    soft17 = False
    if state.total == 17 and ace(state):
        soft17 = True
    return int(state.total >= 17 and not soft17)


class Result(IntFlag):
    dwin = -1
    push = 0   #slang for draw
    pwin = 1


def play_turn(deck, policy, state, ace_reduce=None):
    if state.total >= 21:
        return []
    log = []
    while True:
        a = int(policy(state))
        log.append((copy.deepcopy(state), a))
        ACTIONS[a](deck, state)
        #currently a callback, lazy hack
        if ace_reduce is not None:
            ace_reduce(state)

        stop = state.total >= 21 or a != 0
        if stop:
            break

    return log


def episode(deck, player_pi):

    def revert_aces(cards):
        for card in cards:
            card.value += 10 if card.value == 1 else 0

    #pt - player total, dt - dealer total
    def winner(pt, dt):
        #agent winning conditions
        result = int((pt <= 21 and pt > dt) or (pt <= 21 and dt > 21)) 
        result = int(Result.dwin if result == 0 and pt != dt else result)
        return result

    dealer, player = deal(deck)

    player[0].optotal = dealer.cards[0].value
    dealer.optotal = player[0].total
    if dealer.total < 21 and player[0].total < 21:
        plog = play_turn(deck, player_pi, player[0], ace_reduce)
        dealer.optotal = player[0].total
        dlog = play_turn(deck, dealer_pi, dealer)
    else:
        plog = []
        dlog = []
    result = winner(player[0].total, dealer.total)
    """
    print("---------GAME INFO----------")
    print(f"player total = {player[0].total}")
    print(f"dealer total = {dealer.total}")

    print(f"RESULT: {result}")
    print(f"Player log: {plog}")
    print(f"Dealer log: {dlog}\n")
    """
    revert_aces(player[0].cards)
    return result, plog, dlog


COLORS = [(0xFF, 0x00, 0x00),   #hit = red
          (0x00, 0x00, 0xFF),   #hold = blue
          (0x00, 0x00, 0x00)]   #undefined=black 

#visualize policy based on Q
def visualize_Q(Q):
    color_grid = np.zeros((len(Q), len(Q[0])))
    for pt in len(Q):
        for dt in len(Q[pt]):
            color_grid[pt][dt] = COLORS[np.argmax(Q[pt][dt])]
    plt.imshow(color_grid)


#DO NOT PASS A TRAINING POLICY TO THIS!!
def visualize_policy(policy, ax=None):
    color_grid = [[COLORS[2] for pt in range(22)] for dt in range(12)]
    for dt in range(len(color_grid)):
        for pt in range(len(color_grid[dt])):
            cards = [Card(pt//2, 0), Card(pt - pt//2, 0)]
            state: State = State(cards, pt, dt)
            a = policy(state)
            color_grid[dt][pt] = COLORS[a]
    if ax is None:
        plt.imshow(color_grid)
        plt.xticks(np.arange(0, 22))
        plt.yticks(np.arange(0, 12))
        plt.show()
        return
    ax.imshow(color_grid)

    ax.set_xticks(np.arange(0, 22))
    ax.set_yticks(np.arange(0, 12))

