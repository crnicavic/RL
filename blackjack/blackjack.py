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
    ACE=11 #easier to work with
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
    ace: bool   #has ace?

    def __hash__():
        return hash(astuple(self))


DECK_COUNT = 1
def deck_init(deck_count=1):
    #limit
    l = lambda r : r if r < 10 else 10
    deck = [Card(l(rank), suit) for rank in range(Rank.TWO, Rank.RANK_TOTAL) \
            for suit in range(Suit.SUIT_TOTAL) for _ in range(DECK_COUNT)]
    np.random.shuffle(deck)
    return deck


#rcpt - recipient of the card
def draw(deck, rcpt, count=1):
    for _ in range(count):
        rcpt.cards.append(deck.pop(-1))
        rcpt.total += rcpt.cards[-1].value
        rcpt.ace = rcpt.cards[-1].value == 11


def hold(deck, rcpt, count=1):

    return 0
        

ACTIONS = [draw, hold]


def deal(deck):
    dealer = Hand([], 0, False)
    #dealer draws 2 cards but only one of them will be visible to the player
    draw(deck, dealer, count=2)

    #making it an array for handling splitting
    player = [Hand([], 0, False)]
    draw(deck, player[0], count=2)
    return dealer, player


#player policy, hand = state
def player_pi(hand):
    return np.random.rand() < 0.5

#HIT = 0, HOLD = 1, simple
def dealer_pi(hand):
    return hand.total > 17

#random constant
BUST = 0xFFFF
deck = deck_init()
def game(deck, plog, dlog):
    def play_turn(deck, policy, hand):
        stop = hand.total >= 21
        log = []
        while not stop:
            a = int(policy(hand))
            log.append((copy.copy(hand), a))
            ACTIONS[a](deck, hand)
            hand.total -= 10 * ((hand.ace) and (hand.total > 21))
            stop = hand.total >= 21 or a != 0
        a = a if hand.total <= 21 else BUST
        log.append((copy.copy(hand), a))
        return log

    #pt - player total, dt - dealer total
    def winner(pt, dt):
        #if the player doesn't win, he loses, VEGAS BABY
        pwin = (pt == 21) or (pt < 21 and pt > dt) or (pt < 21 and dt > 21)
        return pwin

    dealer, player = deal(deck)
    plog.append(play_turn(deck, player_pi, player[0]))
    dlog.append(play_turn(deck, dealer_pi, dealer))
    pwin = winner(player[0].total, dealer.total)
    return pwin

def form_Q(deck):
    def experience(turnlog, result, gamma=1):
        rewards = [0 for _ in turnlog]
        rewards[-1] = result
        g = [result]
        for r in rewards[:-1]:
            g.insert(0, g[0]*gamma) 
        exp = []
        for hand, g in zip(turnlog, g):
            exp.append((hand[0].cards, hand[0].total, hand[1], g))
        return exp

    plog, dlog = [], []
    #if player won, reward is 1 otherwise -1
    result = (game(deck, plog, dlog)) * 2 - 1
    print(experience(plog[-1], result, 0.9))
    return 0

form_Q(deck)