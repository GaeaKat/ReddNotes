import os
from datetime import datetime
from pprint import pprint

import asyncpraw.models.user
from dotenv import load_dotenv

from RedditModNotes import ModNoteLabels, ModNoteHumanLabels
from pagination import AutoEmbedPaginator

load_dotenv()

from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import nextcord

reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent="ReddNotes by u/treriri",
    username=os.getenv("REDDIT_USERNAME"),
)

intents = nextcord.Intents().all()
bot = commands.Bot(command_prefix="+", intents=intents)
server = int(os.getenv("DISCORD_SERVER"))
default_sub = os.getenv("DEFAULT_SUBREDDIT")


def create_embed(page: int, user: asyncpraw.models.Redditor) -> nextcord.Embed:
    ret = nextcord.Embed()
    ret.title = "Mod Notes for " + user.name + " page " + str(page)
    ret.description = "Modnotes for user " + user.name
    return ret


async def generate_embed(note: asyncpraw.models.ModNote, embed: nextcord.Embed, note_num: int,
                         justNotes: bool) -> nextcord.Embed:
    embed.add_field(name="Note " + str(note_num + 1), value="----------", inline=False)
    mod_added = await (await note.operator)
    embed.add_field(name="Added By", value=mod_added.name, inline=True)
    if not justNotes:
        embed.add_field(name="Type", value=note.type, inline=True)
    embed.add_field(name="Label",
                    value=ModNoteHumanLabels[note.user_note_data['label']] if note.user_note_data[
                                                                                  'label'] is not None else 'None')
    date_time = datetime.fromtimestamp(note.created_at)
    embed.add_field(name="Time", value=str(date_time))
    embed.add_field(name='Message', value=note.user_note_data['note'], inline=True)
    if note.user_note_data['reddit_id'] is not None:
        url = None
        objects = reddit.info(fullnames=[note.user_note_data['reddit_id']])
        async for object in objects:
            url = object.permalink
        if url is not None:
            embed.add_field(name="Link", value="https://old.reddit.com" + url, inline=True)
        else:
            embed.add_field(name="Link", value="None", inline=True)
    else:
        embed.add_field(name="Link", value="None", inline=True)
    return embed


@bot.slash_command(name='write', description='Writes a modnote to a user', guild_ids=[server])
async def write(interaction: Interaction, user=SlashOption(required=True, description='User to lookup'),
                note=SlashOption(required=True, description='Mod note to leave'),
                label=SlashOption(description='Label to add to note', default='None', choices=ModNoteLabels),
                subreddit=SlashOption(default=default_sub, description='subreddit to use')):
    await interaction.response.send_message('Adding Mod Note now')
    subreddit_obj = await reddit.subreddit(subreddit)
    user_obj = await reddit.redditor(user)
    if label == 'None':
        label = None
    pprint(label)
    notes = await(await subreddit_obj.notes.add(user_obj, note=note, label=label))


@bot.slash_command(name='read', description='Reads mod notes of a user', guild_ids=[server])
async def read(interaction: Interaction, user=SlashOption(required=True, description='User to lookup'),
               subreddit=SlashOption(default=default_sub, description='subreddit to use'),
               just_notes: bool = SlashOption(default=True, description='Should this return only Mod Notes?')):
    # filter: str = SlashOption(description='Filter of label types', choices=ModNoteLabels, default='NONE')):
    await interaction.response.send_message('Reading!')
    subreddit_obj = await reddit.subreddit(subreddit)
    user_obj = await reddit.redditor(user)
    notes = await subreddit_obj.notes(user_obj)
    embeds = [create_embed(1, user_obj)]
    cur_embed = 0
    cur_note = 0
    async for note in notes:
        if note.type == 'NOTE' or not just_notes:
            await generate_embed(note, embeds[cur_embed], (cur_embed * 2) + cur_note, just_notes)
            cur_note = cur_note + 1
            if cur_note > 1:
                cur_note = 0
                cur_embed = cur_embed + 1
                embeds.append(create_embed(cur_embed + 1, user_obj))
    paginator = AutoEmbedPaginator(interaction.channel, bot)

    await paginator.run(embeds)


bot.run(os.getenv("DISCORD_KEY"))
