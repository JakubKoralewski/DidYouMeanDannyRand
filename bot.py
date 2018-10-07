import json
import os
import random
import time
import re

import praw

from bot_helper import *

# Get triggers, answers from JSON file
with open('quotes.json', 'r') as quotes:
    quotes = json.load(quotes)

# Things triggering bot:
all_catches = quotes['catches']
catches = all_catches['basic']
catches_hi = all_catches['hi']

# Answers for triggers:
all_answers = quotes['answers']
answers = all_answers['basic']
answers_hi = all_answers['hi']
#print(f"catch: {catch}\ncomments: {comments}")

# Log in.
reddit = praw.Reddit(user_agent=os.environ['USER_AGENT'],
                     client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'],
                     username=os.environ['REDDIT_USERNAME'], password=os.environ['REDDIT_PASSWORD'])

my_username = reddit.user.me()
print(f"Logged in as {my_username}")

my_username = reddit.user.me()
defenders = reddit.subreddit("Defenders")

for comment in defenders.stream.comments():
    text = comment.body

    # CHECKS:

    # Should not reply to yourself.
    yourself = False
    if comment.author == my_username:
        yourself = True

    # Should not reply twice.
    duplicate = check_if_duplicate(comment.id)

    if not yourself and not duplicate:

        # Don't look in quotes (deleting quotes).
        quotes = re.compile(r'>.+\n\n')
        text = re.sub(quotes,'',text)

        # Get catch words that are in comment.
        # All catch words should not be in comment, 
        # because bot should not correct when someone uses the whole catchphrase!

        all_catches = False

        # For every catchphrase:
        for catch in catches:
            p = re.compile(r'(\S+\s){0,4}\s+'+catch+'\s+(\S+\s){0,4}', re.IGNORECASE)
            [matches.append(match) for match in re.findall(p,text)]
            # Get the parts where someone mentions the Immortal Iron Fist.
            matches = []               
            
            print(matches)
            # Get random answer.
            i = random.randint(0, len(answers)-1)
            #print(f'ANSWER:\n{answers[i]}')
            save_as_duplicate(comment.id)


"""
        print('\n')
        print(contains)
        print(f'_COMMENT:\n{text}')
contains = [catch for catch in catches if catch in text.lower()]
if len(contains)>0:            
            # Get the parts where someone mentions the Immortal Iron Fist
            matches = []
            for word in contains:
                #print(word)
                # Get four words before and four after (or less) of the matching phrase
                p = re.compile(r'(\S+\s){0,4}\s+'+word+'\s+(\S+\s){0,4}', re.IGNORECASE)
                [matches.append(match) for match in re.findall(p,text)]
            
            print(matches)

            # Get random answer
            i = random.randint(0,len(answers)-1)
            #print(f'ANSWER:\n{answers[i]}')
            save_as_duplicate(comment.id)"""
