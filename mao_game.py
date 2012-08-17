import mao_cards as cards
Pile = cards.Pile

class Game:
    def __init__(self):
        piles = self.piles = {}
        self.stack = piles["stack"] = Pile()
        piles["active"] = Pile()
        piles["deck"] = Pile()
        self.players = []
        self.current_player = 0
        self.running = False
    def add_player(self, name):
        if not self.running:
            self.players.append("player_" + name)
    def draw(self, location, count=1):
        latest = []
        stack.append(latest)
        for x in range(count):
            latest.append( self.piles[location].pop() )
