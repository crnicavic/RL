"""
reject OOP, embrace monke
- Let it be clear i regret this statement, classes would have made this so much easier
- The base of the simulator and learning is very simple and i think good
    but adding hacks to make optotals and ace_reducers work ruined everything
    which could have been avoided by using classes
    * which doesn't change the fact that I hate them
"""
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

from enum import IntFlag, Enum

from itertools import repeat

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
    cut = len(deck) // 5
    return deck


#rcpt - recipient of the card
def draw(deck, rcpt, count=1):
    for _ in range(count):
        rcpt.cards.append(deck.pop(-1))
        rcpt.total += rcpt.cards[-1].value


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

#player policy, hand = state
def player_pi(state: State):
    return np.random.rand() < 0.5 if state.total < 21 else 1


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


def episode(deck, plog, dlog):

    #pt - player total, dt - dealer total
    def winner(pt, dt):
        result = int((pt <= 21 and pt > dt) or (pt <= 21 and dt > 21)) #pwin?
        result = int(Result.dwin if result == 0 and pt != dt else result)
        return result

    dealer, player = deal(deck)

    player[0].optotal = dealer.cards[0].value
    dealer.optotal = player[0].total
    if dealer.total < 21 and player[0].total < 21:
        plog.append(play_turn(deck, player_pi, player[0], ace_reduce))
        dealer.optotal = player[0].total
        dlog.append(play_turn(deck, dealer_pi, dealer))
    else:
        plog.append([])
        dlog.append([])
    result = winner(player[0].total, dealer.total)
    print("---------GAME INFO----------")
    print(f"player total = {player[0].total}")
    print(f"dealer total = {dealer.total}")

    print(f"RESULT: {result}")
    print(f"Player log: {plog[-1]}")
    print(f"Dealer log: {dlog[-1]}\n")

    return result


def gatherxp(deck, count=10):

    def logs2xp(turnlog, result, gamma=1):
        xp = []
        #natural blackjack creates an empty log, nothing to learn from that
        if not turnlog:
            return xp
        rewards = [0 for _ in turnlog]
        rewards[-1] = result
        g = [result]
        for r in rewards[:-1]:
            g.insert(0, g[0]*gamma) 
        for (hand, a), g in zip(turnlog, g):
            xp.append((hand, a, g))
        return xp

    plog, dlog = [], []
    xp = []
    wins = 0
    for _ in range(count):
        result = episode(deck, plog, dlog)
        xp.append(logs2xp(plog[-1], result, 0.9)) 
        wins += int(result == 1)
            
    return xp

def calculate_Q(xp):
    G = np.zeros((22, 12, len(ACTIONS), 0)).tolist()
    Q = np.zeros((22, 12, len(ACTIONS))).tolist()
    for ep in xp:
        for (state, a, g) in ep:
            G[state.total][state.optotal][a].append(g)

deck = deck_init(6)
xp = gatherxp(deck)
calculate_Q(xp)

