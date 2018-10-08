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

corrects = ["iron fist", "protector of ", "sworn enemy of the hand"]
corrects_kunlun = ["kunlun","k'un-lun","kun-lun"]

# Log in.
reddit = praw.Reddit(user_agent=os.environ['USER_AGENT'],
                     client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'],
                     username=os.environ['REDDIT_USERNAME'], password=os.environ['REDDIT_PASSWORD'])

my_username = reddit.user.me()
print(f"Logged in as {my_username}")

defenders = reddit.subreddit("Defenders")

EXAMPLE_COMMENTS = [
    """> THIS IS A COMMENT

    NOT TAlking about if""",
    """alalal al lal las i am talking about the Iron FIST""",
    """immortal Iron Fist, protector of Kunlun, sworn enemy of the hand""",
    """ danny rand """,
    """ SOMETHIN SOMETHING HERE COMES A RANDOM GREATER tahn > and talking more

    gut shit danny rand"""

]


for comment in defenders.stream.comments():
    text = comment.body


    # CHECKS:

    # Should not reply to yourself.
    yourself = False
    
    if comment.author == my_username:
        yourself = True

    duplicate = False
    # Should not reply twice.
    duplicate = check_if_duplicate(comment.id)
    print(f'duplicate: {duplicate}')

    if not yourself and not duplicate:
        
        # Delete quotes
        quotes = re.compile(r'(?<=\n)|(?<=^)>.+\n')
        text = re.sub(quotes,'',text)

        #print('______________________________AFTERQUOTES\n',text)

        # Get catch words that are in comment.
        all_matches = []
        for catch in catches:
            # Get the parts where someone mentions the Immortal Iron Fist by the list(catches).
            p = re.compile(r'(\S+\s){0,4}(' + catch + r')\s?(\S+\s){0,4}', re.IGNORECASE)
            matches = re.finditer(p, text)
            if matches: 
                for quote in matches:
                    all_matches.append([catch,quote])
        
        # if no catch then don't bother
        if not all_matches:
            continue
        save_as_duplicate(comment.id)
        print('\n\n',text)

        # All catch words should not be in comment, 
        # because bot should not correct when someone uses the whole catchphrase!
        correctness = re.compile(r'{iron}..?({protector}({k1}|{k2}|{k3}))..?{sworn}'.format(
            iron=corrects[0],protector=corrects[1],sworn=corrects[2],k1=corrects_kunlun[0],k2=corrects_kunlun[1],k3=corrects_kunlun[2]),re.IGNORECASE)
        is_correct = True if re.search(correctness,text) else False

        print(f'is_correct: {is_correct}')
        if not is_correct:
            for match in all_matches: 
                catch = match[0]
                quote = match[1]
                ai_answer = f"Who is {quote.group(2)}?"


                # Get random answer index.
                i = random.randint(0, len(answers)-1)
                
                quote = bold_quote(catch, quote[0])
                answer = f"""> {quote}

{ai_answer} {answers[i]}
                """
                print(f'\nANSWER:\n {answer}')

