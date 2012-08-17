import socket
from mao_game import Game
import irc_config as config
import time



def parse_message(message):
    """Takes an incoming message (full, IRC style) and splits it into a tuple
    of (prefix, message type, body) as defined in the RFC."""
    if message == "":
        return ("", "", "")
    elif message[0] == ":":
        split_message = message.split(" ", 1)
        prefix = split_message[0]
        (message_type, body) = split_message[1].split(" ", 1)
    else:
        split_message = message.split(" ", 1)
        prefix = ""
        message_type = split_message[0]
        body = split_message[1]
    return (prefix, message_type, body)

class irc_bot:
    "Handles the IRC connection, as well as game state."
    def __init__(self):
        self.nick = config.nick
        self.access_pw = "blocky" #Remember to change this for other implementations.
        self.access_list = set([ "SoobNauce" ])
        self.games = {}
        self.connection = socket.socket()
        self.buffer = ""
        self.config_options = {"notice": True, "chanstatus": True, "reject": "both"}
    def connect(self):
        self.connection.connect( (config.server, config.port) )
        self.send_data("NICK {n}".format(n=self.nick), "")
        self.send_data("USER SoobNauce 8 *", " SoobNauce")
        self.send_data("MODE {n} +B".format(n=self.nick), "")
        self.get_messages()
    def get_messages(self):
        self.buffer += self.connection.recv(512)
        while self.buffer[-2:] != "\r\n":
            self.buffer += self.connection.recv(512)
        self.process_buffer()
    def process_buffer(self):
        if len(self.buffer) < 2:
            return
        while self.buffer[-2:] != "\r\n":
            self.buffer += self.connection.recv(512)
        queue = self.buffer.split("\r\n")
        self.buffer = ""
        for message in queue:
            self.process_message( message )
    def process_message(self, message ):
        (prefix, command, body) = parse_message(message)
        if command == "PING":
            ping_reply = body.split(":",1)[1]
            self.send_data( "PONG", ping_reply )
        else:
            command_parts = command.split(" ")
            if command_parts[0] == "PRIVMSG":
                self.process_privmsg( (prefix, command, body) )
    def process_privmsg(self, (prefix, command, body) ):
        user_from = prefix.split("!", 1)[0][1:]
        (channel, message) = body.split(" :", 1)
        if channel == self.nick:
            print "User {f} sent a private message:\n\t{m}".format(f=user_from, m=message)
        else:
            print "User {f} sent a message in {c}:\n\t{m}".format(f=user_from, m=message, c=channel)
        if message[0] == "\x01":
            self.process_ctcp( message, user_from )
        elif message[0] == "!":
            self.process_command( message, user_from, channel )
        else:
            self.scan_chatter( message, user_from, channel )
    def process_ctcp( self, message, user_from ):
        split_message = message.split(" ")
        if split_message[0] == "\x01VERSION\x01":
            print "VERSION requested"
            self.send_data( "", "NOTICE {f}".format(f=user_from), "\x01VERSION Custom, using python.socket\x01")
        elif split_message[0] == "\x01PING":
            print "PING requested"
            self.send_data( "", "NOTICE {f}".format(f=user_from), message )
    def process_command( self, message, user, channel ):
        print "{u} used command (sent to {c}).  Message:\n\t{m}".format(u=user, c=channel, m=message)
        split_msg = message.split(" ", 1)
        if len(split_msg) == 1:
            command = split_msg[0]
            args = ""
        else:
            (command, args) = split_msg
        if command == "!auth":
            if user not in self.access_list:
                if args == self.access_pw:
                    self.access_list.add(user)
                    self.respond( "User {u} added to access list.".format(u=user), user )
                else:
                    self.respond( "Password incorrect", user )
            else:
                self.respond( "You are already on the access list.", user )
        elif command == "!deauth":
            if user in self.access_list:
                self.access_list.remove(user)
                self.respond( "You are no longer authorized", user )
        elif command == "!echo":
            if self.access_check(user):
                self.send_data( "PRIVMSG {}".format(channel), args )
        elif command == "!join_c":
            if self.access_check(user):
                self.send_data( "JOIN {}".format(args), "" )
        elif command == "!part":
            if self.access_check(user):
                self.send_data( "PART {}".format(args), "" )
        elif command == "!disconnect":
            if self.access_check(user):
                self.send_data( "QUIT Going down", "" )
        elif command == "!op":
            if args == "":
                target = user
            else:
                target = args
            if self.access_check(user):
                if channel != self.nick:
                    self.send_data("MODE {c} +o {n}".format(c=channel, n=target), "")
                else:
                    self.respond("Wrong channel", user)
        elif command == "!deop":
            if args == "":
                target = user
            else:
                target = args
            if self.access_check(user):
                if channel != self.nick:
                    self.send_data("MODE {c} -o {n}".format(c=channel, n=target), "")
                else:
                    self.respond("Wrong channel", user)
        elif command == "!kick":
            split_args = args.split(" ", 1)
            if args == "":
                target = user
                reason = "You asked for it"
            elif len(split_args) == 1:
                target = args
                reason = user
            else:
                target = split_args[0]
                reason = split_args[1]
            if self.access_check(user):
                if channel != self.nick:
                    self.send_data("KICK {c} {n} {r}".format(c=channel, n=target, r=reason), "")
                else:
                    self.respond( "Wrong channel", user )
            elif channel != self.nick:
                self.send_data("KICK {c} {n} And thou shalt love the Lord thy God with all thy heart, and with all thy soul, and with all thy mind, and with all thy strength".format(c=channel, n=user), "")
        elif command in [ "!setup", "!scoreboard", "!join", "!begin", "!abort", "!status", "!hand", "!play", "!draw", "!reject", "!boot", "!quit", "!advance", "!refresh" ]:
            if command in ["!play", "!draw", "!reject"]:
                (arg_part, msg_part) = args.split(";", 1)
                self.game_command( command, arg_part , user, channel)
                self.scan_chatter( msg_part, user, channel )
            else:
                self.game_command( command, args, user, channel )
        elif command == "!list_commands":
            self.respond( "auth [pw], deauth, echo [text], join_c [channel], part [channel], disconnect, op [user], deop [user], kick [user], setup, scoreboard, join, begin, abort, status, hand, play [position], draw [count=1], reject, boot [player], quit, advance, refresh", user)
            self.respond( "Commands requiring authorization: deauth, echo [text], join_c [channel], part [channel], disconnect, op [user], deop [user], disconnect, op [user], deop [user], kick [user], boot [player], refresh", user)
            self.respond( "Commands not requiring authorization: list_commands, help [command], setup, scoreboard, join, begin, abort, status, hand, play [position], draw [count=1], reject, quit, advance", user)
            self.respond( "Commands that must be used in a channel: op [user], deop [user], kick [user], setup, join, begin, abort, play [position], draw [count=1], reject, boot [player], quit, advance, refresh", user)
    def access_check(self, user):
        if user in self.access_list:
            return True
        else:
            self.respond( "Only users on the access list can use that command.", user )
            return False
    def respond(self, response, dest):
        if self.config_options["notice"]:
            self.send_data( "NOTICE {}".format(dest), response )
        else:
            self.send_data( "PRIVMSG {}".format(dest), response )
    def send_data(self, first, second, third = False):
        if third == False:
            if second == "":
                line = "{f}\r\n".format(f=first)
            else:
                line = "{f} :{s}\r\n".format(f=first, s=second)
        else:
            line = ":{f} {s} :{t}\r\n".format(f=first, s=second, t=third)
        status_msg = "Sending:\n\t{l}".format(l=line)
        print status_msg
        self.connection.send(line)
    def send_message(self, message, dest):
        if dest == "":
            com_str = "PRIVMSG"
        else:
            com_str = "PRIVMSG {x}".format(x=dest)
        self.send_data( com_str, message )
    #Action format is \x01ACTION [action]\x01
    #Game code goes below this line
    def game_command(self, command, args, user, channel):
        #TODO
        print "Game command in {c} by {u}:\n\t{m} -> {a}".format(c=channel,u=user,m=command,a=args)
    def scan_chatter(self, message, user, channel):
        #TODO
        print "Scanning chatter for rules:\n\t{u} said in {c} \"{m}\"".format(u=user, c=channel, m=message)
    #Game code above this line
if __name__ == "__main__":
    mao = irc_bot()
    mao.connect()
    while True:
        mao.get_messages()
