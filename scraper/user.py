import discord


class ScraperUser:
    def __init__(self, user: discord.User):
        self.user = user
        self.months_subscribed: list[tuple[str, int]] = []
        self.games_redeemed: list[tuple[str, str, int]] = []
