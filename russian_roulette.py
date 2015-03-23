# coding=utf8
"""
russian_roulette.py - A Russian Roulette bot for Willie
Copyright 2015, Kharidiron [kharidiron@gmail.com]
"""

from __future__ import unicode_literals

from willie.module import commands, example
import random

def setup(bot):
    bot.memory["rr_game"] = RussianRoulette(bot)

@commands("rr")
def manage_game(bot, trigger):
    """Russian Roulette minigame. For an intro on how to play, type .rr help"""
    bot.memory["rr_game"].manage_game(bot, trigger)

class RussianRoulette:
    def __init__(self, bot):
        self.running = False
        self.spun = False
        self.players = {}
        self.current_game = []
        self.chamber = "o"
        self.cartridge = {1:"o",
                          2:"o",
                          3:"o",
                          4:"o",
                          5:"o",
                          6:"o"}
        self.rounds = 0
        # Flavor text stolen from someone else's RR game
        self.deaths = ("blasts their brains onto the wall.", "looks startled.",
                       "ruins the furniture.", "meets his ancestors.",
                       "ventilates the head.", "scores 1 point.",
                       "- in Soviet Russia, gun levels you.",
                       "splatters across the channel.", "meets his RNG.",
                       "slays two ears with one shot.", " <=|= [HEADSHOT]",
                       "learned a lesson about fortuitousness.", "drops dead.")

        # generate list of all actions
        self.actions = sorted(method[4:] for method in dir(self)
                              if method[:4] == "_rr_"
                              and method[:6] != "_rr_a_")
        self.admin_actions = sorted(method[6:] for method in dir(self)
                                    if method[:6] == "_rr_a_")

    def _show_doc(self, bot, command, isadmin):
        """Print the docstring for a command"""
        if isadmin:
            for line in getattr(self, "_rr_a_" + command).__doc__.split("\n"):
                line = line.strip()
                if line:
                    bot.reply(line)
        else:
            for line in getattr(self, "_rr_" + command).__doc__.split("\n"):
                line = line.strip()
                if line:
                    bot.reply(line)

    def manage_game(self, bot, trigger):
        """Manage the Russian Roulette game. Usage: .rr <command>"""
        args = trigger.group().split()
        if (len(args) < 2 or args[1] not in self.actions
            and args[1] not in self.admin_actions):
            bot.reply("Usage: .rr <command>")
            bot.reply("Available commands: " + ", ".join(self.actions))
            if trigger.admin:
                bot.reply("Available admin commands: " +
                          ", ".join(self.admin_actions))
            return

        if args[1] in self.actions:
            if getattr(self, "_rr_" + args[1])(bot, trigger):
                pass
            return

        if args[1] in self.admin_actions:
            if getattr(self, "_rr_a_" + args[1])(bot, trigger):
                bot.say("admin command called")
            return

    def _rr_join(self, bot, trigger):
        """Join in the current game."""
        if not self.running:
            if trigger.nick not in self.players:
                self.players[trigger.nick] = {"wins":0,
                                            "losses":0,
                                            "flees":0,
                                            "streak":0}
            if trigger.nick not in self.current_game:
                self.current_game.append(trigger.nick)
                bot.say("%s has joined the game." % trigger.nick)
            else:
                bot.reply("You're already playing.")
        else:
            bot.reply("There is already a game in progress. Please wait.")

    def _rr_quit(self, bot, trigger):
        """Wimp out of the current game."""
        if self.running:
            if trigger.nick in self.current_game:
                self.current_game.remove(trigger.nick)
                self.players[trigger.nick]["flees"] += 1
                bot.say("%s is wimping out." % trigger.nick)
            else:
                bot.reply("You weren't playing to begin with.")
        else:
            if trigger.nick in self.current_game:
                self.current_game.remove(trigger.nick)
                bot.say("%s is opting out of the next round." % trigger.nick)
            else:
                bot.reply("You weren't playing to begin with.")

    def _rr_players(self, bot, trigger):
        """List the current players."""
        if self.current_game:
            bot.say(" ,".join(self.current_game))
        else:
            bot.say("No one is currently playing.")

    def _rr_start(self, bot, trigger):
        """Start the game"""
        if not self.current_game:
            bot.say("Some people need to join the game first.")
            return

        if self.rounds == 0:
            bot.say("You might want to load the gun first.")
            return

        if not self.running:
            bot.say("Here is the turn order:")
            bot.say(", ".join(self.current_game))
            bot.say("Let the games being.")
            self.running = True
        else:
            bot.say("A game is already in progress.")

    def _rr_stop(self, bot, trigger):
        """Stop the game"""
        if self.running:
            bot.say("The round has been ended early.")
            self.running = False

    def _rr_load(self, bot, trigger):
        """Load a bullet into the gun."""
        if self.running:
            bot.say("This round is already started, please wait till the next.")
            return

        if len(trigger.group(2).split()) == 1:
            rounds = 1
        else:
            rounds = int(trigger.group(2).split()[1])

        if rounds < 7:
            if self.rounds + rounds <= 6:
                self._load_bullet(rounds)
            else:
                bot.say("This gun only holds six rounds, and there are already "
                        + str(self.rounds) + " rounds in it.")
        else:
            bot.say("The gun only holds six rounds.")

        if self.rounds == 6:
            bot.say("The gun is fully loaded. This is probably a bad idea...")

    def _load_bullet(self, rounds):
        for bullet in range(rounds):
            self.rounds += 1
            self.cartridge[self.rounds] = "x"

    def _rr_empty(self, bot, trigger):
        """Empty the gun."""
        if self.running:
            bot.say("Please stop the round before emptying the gun.")
            return

        self.spun = False
        self.rounds = 0
        self.chamber = "o"
        self.cartridge = {1:"o",
                          2:"o",
                          3:"o",
                          4:"o",
                          5:"o",
                          6:"o"}
        bot.say("%s emptied the gun" % trigger.nick)

    def _rr_spin(self, bot, trigger):
        """Sping the cartridge."""
        if not self.running:
            pass

    def _rr_pull(self, bot, trigger):
        """Pull the trigger."""
        if not self.running:
            pass

    def _rr_pass(self, bot, trigger):
        """Pass the gun to the next person."""
        if not self.running:
            pass

    def _rr_score(self, bot, trigger):
        """Check the current score."""
        if self.players:
            bot.say("Here are the scores:")
            for player in self.players:
                bot.say(player + " has " +
                        str(self.players[player]["wins"]) + " wins, " +
                        str(self.players[player]["losses"]) + " losses, " +
                        "has fled " + str(self.players[player]["flees"]) +
                        " times, and a longest streak of " +
                        str(self.players[player]["streak"]) + " rounds.")
        else:
            bot.say("No one has played yet.")

    def _rr_a_check(self, bot, trigger):
        """Check the status of the gun."""
        if trigger.admin:
            bot.say("rounds loaded: " + str(self.rounds) + "  " +
                    "cartidge spun: " + str(self.spun) + "  " +
                    "cartridge: " + str(self.cartridge) + "  " +
                    "chamber: " + str(self.chamber))

    def _rr_a_reset(self, bot, trigger):
        """Reset all values in the current game."""
        pass

    def _rr_help(self, bot, trigger):
        """Get help on playing Russian Roulette. Usage: .rr help <command>"""
        command = trigger.group(4)
        if command in self.actions:
            self._show_doc(bot, command, False)
        elif command in self.admin_actions and trigger.admin:
            self._show_doc(bot, command, True)
        else:
            bot.reply("For help on a command, type: .rr help <command>")
            bot.reply("Available commands: " + ", ".join(self.actions))
        pass
