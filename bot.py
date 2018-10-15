import json
import os
import random
import time
import re
import asyncio

import praw


class BreakLoop(Exception):
    pass


async def check_comments(sub):
    print(f'starting in: {sub}')
    for comment in sub.stream.comments(pause_after=0):
        if comment is None:
            break
        try:
            print(f'checking {sub}')
            await subreddit_search(comment)
        except BreakLoop:
            pass
        await asyncio.sleep(0.1)


async def subreddit_search(comment):

    text = comment.body
    # CHECKS:
    # Should not reply to yourself.
    yourself = True if comment.author == my_username else False
    if yourself:
        raise BreakLoop

    # Should not reply twice.
    duplicate = check_if_duplicate(comment.id)
    if duplicate:
        raise BreakLoop

    # Delete quotes
    quotes = re.compile(r'(?<=\n)|(?<=^)>.+\n')
    text = re.sub(quotes, '', text)

    # Get catch words that are in comment.
    all_matches = []
    for catch in catches:

        # Get the parts where someone mentions the Immortal Iron Fist by the list(catches).
        p = re.compile(
            r'(\S+\s){0,4}(' + catch + r')\s?(\S+\s){0,4}', re.IGNORECASE)
        matches = re.finditer(p, text)

        await asyncio.sleep(0.01)

        if matches:
            for quote in matches:
                all_matches.append([catch, quote])

    # if no catch then don't bother or if more or equal to three of the matches
    # All catch words should not be in comment,
    # because bot should not correct when someone uses the whole catchphrase!
    save_as_duplicate(comment.id)
    if not all_matches or len(all_matches) >= 3:
        print('not all_matches or len(all_matches>=3')
        print(all_matches)
        raise BreakLoop

    print(all_matches)
    print('\n\n', text)

    for match in all_matches:

        catch = match[0]
        quote = match[1]
        ai_answer = f"Who is {quote.group(2)}?"

        # Get random answer.
        i = random.randint(0, len(answers)-1)
        quote = bold_quote(catch, quote[0])
        await asyncio.sleep(0.01)

    answer = f"> {quote}\n\n{ai_answer} {answers[i]}"
    print(f'\nANSWER:\n {answer}')


def save_as_duplicate(id):
    print(f"Saving id:'{id}' as duplicate", end="")
    with open('commented.txt', 'a+') as commented:
        print(" to file...")
        commented.write(id + ',')


def check_if_duplicate(id):
    # if file containing duplicates doesn't exist:
    # its not a duplicate -> finish execution
    exists = os.path.exists('commented.txt')
    if not exists:
        return False

    with open('commented.txt', 'r') as commented:
        commented = commented.read().split(',')
        for otherid in commented:
            otherid = otherid.strip()
            if otherid == id:
                return True

    return False


def bold_quote(catch, quote):
    bolded = f'**{catch}**'
    quote = re.sub(catch, bolded, quote)
    return quote


def test_comments():
    with open('testcomments.txt', 'r') as c:
        comments = c.read().split(',')
    return comments


async def main():

    defenders = reddit.subreddit("Defenders")
    marvelstudios = reddit.subreddit("marvelstudios")

    await asyncio.gather(
        check_comments(defenders),
        check_comments(marvelstudios),)


# Log in.
reddit = praw.Reddit(user_agent=os.environ['USER_AGENT'],
                     client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'],
                     username=os.environ['REDDIT_USERNAME'], password=os.environ['REDDIT_PASSWORD'])

my_username = reddit.user.me()
print(f"Logged in as {my_username}")

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

start = time.time()
max_run_time = 5

asyncio.run(main())
