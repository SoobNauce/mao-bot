import random
shuffle = random.shuffle

def say_suit( card ):
    "Returns the string representation of the suit of the given card"
    return name_suit( ( (card-1)/13 ) )
def name_suit( x ):
    """Returns the string representation of the given suit number (0, 1, 2, 3).
Unexpected suits are wild."""
    if x == 0: return "Spades"
    elif x == 1: return "Hearts"
    elif x == 2: return "Diamonds"
    elif x == 3: return "Clubs"
    else: return "Wild"

def say_val(card):
    "Returns the string representation of the value of the given card"
    return name_val( ( card % 13)+1 )
def name_val(x):
    """Returns the string representation of the given value.
    Jokers should be handled elsewhere, due to their not having a suit."""
    if x == 1: return "Ace"
    elif 2 <= x <= 10: return str(x)
    elif x == 11: return "Jack"
    elif x == 12: return "Queen"
    elif x == 13: return "King"
    else: return "Wild"

def short_card( card ):
    """Gives a two-character representation of the given card.
Examples of strings returned by this are XH (10 of hearts), ?B (black joker), and 8S (8 of spades)"""
    card = card % 54
    if card == 54:
        return "?R"
    elif card == 53:
        return "?B"
    else:
        c_suit = say_suit(card)[0].upper()
        c_v = say_val(card)
        if c_v == "10":
            c_val = "X"
        else:
            c_val = c_v[0]
    return "{v}{s}".format(v=c_val, s=c_suit)
def say_card( card ):
    "Describes the given card in human-readable terms."
    deck = 0
    deck = (card-1) / 54
    card = card % 54
    if card == 54:
        c_part = "Red Joker"
    elif card == 53:
        c_part = "Black Joker"
    else:
        c_part = "{val} of {suit}".format( val=say_val(card), suit=say_suit(card) )
    if deck > 0:
        string = "{c} ({d})".format(c=c_part, d=deck)
    else:
        string = c_part
    return string

def new_deck(jokers = False, number = 0):
    """Creates a new deck, as a pile.  Optionally, adds jokers, or
tags the deck with a number."""
    begin = 1 + (number * 54)
    if jokers:
        end = 55 + (number * 54)
    else:
        end = 53 + (number * 54)
    x = Pile( [c for c in range(begin, end)] )
    shuffle(x)
    return x


class Pile(list):
    """Keeps track of cards, adding methods on top of list methods
such as push, and two functions (place/take) using positions instead of indices"""
    def __init__(self, seed=[]):
        super(list, self)
        self += seed
    def __repr__(self):
        return "Pile( [{data}] )".format(data = str(list(self)))
    def push(self, card, index=-1):
        """Adds the card to the top of the deck
(use insert or place to name an index)"""
        self.insert(card)
    def place(self, position, card):
        """A wrapper around insert, using a position instead of an index"""
        self.insert(position-1, card)
    def take(self, position):
        """A wrapper around pop, using a position instead of an index"""
        return self.pop(position-1)
