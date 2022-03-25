import asyncio

import nextcord
from nextcord.ext import commands


class AutoEmbedPaginator(object):
    def __init__(self, channel: nextcord.TextChannel,bot:commands.Bot, **kwargs):
        self.embeds = None
        self.bot = bot
        self.channel = channel
        self.current_page = 0
        self.auto_footer = kwargs.get("auto_footer", False)
        self.remove_reactions = kwargs.get("remove_reactions", False)
        self.control_emojis = ('⏮️', '⏪', '🔐', '⏩', '⏭️')
        self.timeout = int(kwargs.get("timeout", 60))
    async def run(self, embeds):
        send_to = self.channel
        wait_for = send_to
        if not self.embeds:
            self.embeds = embeds
        if self.auto_footer:
            self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
        msg = await send_to.send(embed=self.embeds[0])
        for emoji in self.control_emojis:
            try:
                await msg.add_reaction(emoji)
            except:
                pass
        msg = await msg.channel.fetch_message(msg.id)
        def check(reaction, user):
            return reaction.message.id == msg.id and str(reaction.emoji) in self.control_emojis
        while True:
            if self.timeout > 0:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add",check=check, timeout=self.timeout)
                except asyncio.TimeoutError:
                    self.current_page = 0
                    for reaction in msg.reactions:
                        if reaction.message.author.id == self.bot.user.id:
                            try:
                                await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                            except:
                                pass
                    return msg
                    break
            else:
                reaction, user = await self.bot.wait_for("reaction_add",check=check)
            if str(reaction.emoji) == self.control_emojis[0]:
                self.current_page = 0
                if self.remove_reactions:
                    try:
                        await msg.remove_reaction(str(reaction.emoji), user)
                    except:
                        pass
                if self.auto_footer:
                    self.embeds[0].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[0])
            elif str(reaction.emoji) == self.control_emojis[1]:
                self.current_page = self.current_page-1
                self.current_page = 0 if self.current_page<0 else self.current_page
                if self.remove_reactions:
                    try:
                        await msg.remove_reaction(str(reaction.emoji), user)
                    except:
                        pass
                if self.auto_footer:
                    self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[self.current_page])
            elif str(reaction.emoji) == self.control_emojis[2]:
                self.current_page = 0
                for reaction in msg.reactions:
                    try:
                        if reaction.message.author.id == self.bot.user.id:
                            await msg.remove_reaction(str(reaction.emoji), reaction.message.author)
                    except:
                        pass
                return msg
                break
            elif str(reaction.emoji) == self.control_emojis[3]:
                self.current_page = self.current_page + 1
                self.current_page = len(self.embeds)-1 if self.current_page > len(self.embeds)-1 else self.current_page
                if self.remove_reactions:
                    try:
                        await msg.remove_reaction(str(reaction.emoji), user)
                    except:
                        pass
                if self.auto_footer:
                    self.embeds[self.current_page].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[self.current_page])
            elif str(reaction.emoji) == self.control_emojis[4]:
                self.current_page = len(self.embeds)-1
                if self.remove_reactions:
                    try:
                        await msg.remove_reaction(str(reaction.emoji), user)
                    except:
                        pass
                if self.auto_footer:
                    self.embeds[len(self.embeds)-1].set_footer(text=f'({self.current_page+1}/{len(self.embeds)})')
                await msg.edit(embed=self.embeds[len(self.embeds)-1])