import mao_cards as cards
import os.path
Pile = cards.Pile

class Game:
    """Game objects are responsible for keeping track of everybody's cards,
scores, and eventually, rules."""
    def __init__(self):
        piles = self.piles = {}
        self.stack = piles["stack"] = Pile()
        piles["active"] = Pile()
        piles["deck"] = Pile()
        self.players = []
        self.current_player = 0
        self.running = False
        self.scoreboard = {}
        self.rules = []
        self.status_queue = []
    def save_scoreboard(self, filename):
    "Saves the scoreboard to a file."
        player_records = []
        for player in self.scoreboard.keys():
            player_records.append( "{0}:\t{1}".format(player, self.scoreboard[player]) )
        file_body = player_records.join("\n")
        scoreboard_file = open(filename, "w")   
        scoreboard_file.write(file_body)
        scoreboard_file.close()
    def load_scoreboard(self, filename):
    "Loads the scoreboard from a file."
        self.scoreboard = {}
        scoreboard_file = open(filename, "r")
        scoreboard_data = scoreboard_file.readlines()
        scoreboard_file.close()
        for player_line in scoreboard_data:
            (player, score) = player_line.split(":\t", 1)
            self.scoreboard[player] = int(score)
#    def export_rules(self, filename):
#    def import_rules(self, filename):
    def add_player(self, name):
        "Adds a player to the game"
        if not self.running:
            self.players.append("player_" + name)
    def draw(self, location=None, count=1):
        "Draws cards from the deck, or the given pile, and adds them to the stack"
        if location == None:
            location = self.piles["stack"]
        latest = []
        self.stack.append(latest)
        for x in range(count):
            latest.append( self.piles[location].pop() )
    def give(self, location):
        "Removes a set of cards from the stack, and merges it with the given pile"
        if len(self.stack) > 0:
            cards = self.stack.pop()
        else:
            return "Empty stack"
        if location in piles.keys():
            piles[location] += cards
            return "Success"
        else:
            self.stack.append(cards)
            return "Wrong player"
    def start_game(self):
        if len(self.players) < 2:
            self.status_msg( "Couldn't start game: too few players" )
        elif self.running:
            self.status_msg( "Couldn't start game: already running" )
        else:
            self.running = True
            self.draw(1)
            self.give(piles["active"])
            self.status_msg( "Game started!" )
    def show_status(self):
        
    def status_msg(self, message):
        self.status_queue.append( message )
