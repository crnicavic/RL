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

def draw(deck, hand):
    draw = deck.pop(-1)
    total += draw.value

        
    return draw

DECK_COUNT = 1
deck = [Card(rank, suit) for rank in range(Rank.TWO, Rank.RANK_TOTAL) \
        for suit in range(Suit.SUIT_TOTAL) for _ in range(DECK_COUNT)]
np.random.shuffle(deck)


