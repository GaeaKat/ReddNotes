from nextcord.ext import commands

from enum import Enum

ModNoteLabels = {'Bot Ban': 'BOT_BAN', 'Perma Ban': 'PERMA_BAN', 'Ban': 'BAN', 'Abuse Warning': 'ABUSE_WARNING',
                 'Spam Warning': 'SPAM_WARNING', 'Spam Watch': 'SPAM_WATCH', 'Solid Contributer': 'SOLID_CONTRIBUTOR',
                 'Helpful User': 'HELPFUL_USER', 'None': 'None'}
ModNoteHumanLabels = {v: k for k, v in ModNoteLabels.items()}



