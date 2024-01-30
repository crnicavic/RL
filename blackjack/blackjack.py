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

from enum import IntFlag, Enum

from itertools import repeat

import copy

"""
Repeat the functionality of this notebook using more realistic Blackjack rules. 
For example, in the actual game of Blackjack each player immediately gets two cards 
(however, only one of the dealer's cards is known to the player, before the player finishes his/hers turn).
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
class Hand:
    cards: [Card]
    total: int

    def __hash__():
        return hash(astuple(self))


DECK_COUNT = 1
def deck_init(deck_count=1):
    #limit
    l = lambda r : r if r <= 11 else 10
    deck = [Card(l(rank), suit) for rank in range(Rank.TWO, Rank.RANK_TOTAL) \
            for suit in range(Suit.SUIT_TOTAL) for _ in range(DECK_COUNT)]
    np.random.shuffle(deck)
    return deck


#rcpt - recipient of the card
def draw(deck, rcpt, count=1):
    for _ in range(count):
        rcpt.cards.append(deck.pop(-1))
        rcpt.total += rcpt.cards[-1].value


def hold(deck, rcpt, count=1):
    return 0
        

ACTIONS = [draw, hold]


def deal(deck):
    
    def ace(hand):
        ace = [card.value == 11 for card in hand.cards]
        return True in ace

    dealer = Hand([], 0)
    #dealer draws 2 cards but only one of them will be visible to the player
    draw(deck, dealer, count=2)

    soft17 = False
    if dealer.total == 17 and ace(dealer):
        soft17 = True

    #making it an array incase I want to add spliting
    player = [Hand([], 0)]
    draw(deck, player[0], count=2)
    return dealer, player, soft17

#player policy, hand = state
def player_pi(hand):

    #reduce the value of an ace if the player is about to bust
    def ace_reduce(hand):
        if hand.total <= 21:
            return
        c_id = 0
        while hand.total > 21 and c_id < len(hand.cards):
            card = hand.cards[c_id]
            hand.total -= 10 if card.value == 11 else 0
            card.value -= 10 if card.value == 11 else 0
            c_id += 1

    ace = ace_reduce(hand)
    return np.random.rand() < 0.5 if hand.total < 21 else 1


#HIT = 0, HOLD = 1, simple
def dealer_pi(hand, soft17=False):
    return int(hand.total >= 17 and not soft17)

class Result(IntFlag):
    dwin = -1
    push = 0   #slang for draw
    pwin = 1


#TODO: ACE REDUCE WILL NEVER BE EXECUTED DUE TO SHIT LOOP, should work now
def play_turn(deck, policy, hand):
    stop = hand.total >= 21
    log = []
    a = int(policy(hand))
    while True:
        log.append((copy.deepcopy(hand), a))
        ACTIONS[a](deck, hand)
        #a can change only from hit to hold, necessary for stochastic policies
        a = int(policy(hand)) + int(a - 1 >= 0)
        stop = hand.total >= 21 or a != 0
        if stop:
            break

    #NOTE: The log will be empty in case of a natural blackjack        
    return log


deck = deck_init()
def episode(deck, plog, dlog):

    #pt - player total, dt - dealer total
    def winner(pt, dt):
        #player won?
        result = Result(int((pt <= 21 and pt > dt) or (pt <= 21 and dt > 21)))
        #if it's not a draw, the dealer won
        result = Result.dwin if result == 0 and pt != dt else result
        return result

    dealer, player = deal(deck)
    #there is nothing to learn from a natural 21, except that someone is lucky
    if dealer.total < 21 and player[0].total < 21:
        plog.append(play_turn(deck, player_pi, player[0]))
        dlog.append(play_turn(deck, dealer_pi, dealer))
    result = winner(player[0].total, dealer.total)
    print("---------GAME INFO----------")
    print(f"player total = {player[0].total}")
    print(f"dealer total = {dealer.total}")

    print(f"RESULT: {result}")
    print(f"Player log: {plog}")
    print(f"Dealer log: {dlog}\n")

    return result



def form_Q(deck):
    def experience(turnlog, result, gamma=1):
        rewards = [0 for _ in turnlog]
        rewards[-1] = result
        g = [result]
        for r in rewards[:-1]:
            g.insert(0, g[0]*gamma) 
        exp = []
        for (hand, a), g in zip(turnlog, g):
            exp.append((hand, a, g))
        return exp

    G = dict[Hand, tuple[list[float], list[float]]]
    plog, dlog = [], []
    #if player won, reward is 1 otherwise -1
    result = episode(deck, plog, dlog)
    if plog:
        ep = experience(plog[-1], result, 0.9)
        print(*ep, sep="\n")       

form_Q(deck)
