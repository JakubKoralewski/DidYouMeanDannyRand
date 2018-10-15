import json
import os
import random
import time
import re
import asyncio

import praw

duplicate_comments = 'duplicate_comments.txt'
duplicate_titles = 'duplicate_titles.txt'


async def check_comments(sub):
    print(f'starting in: {sub}')
    for comment in sub.stream.comments(pause_after=0):
        if comment is None:
            break
        print(f'checking {sub}')
        await comment_search(comment)
        await asyncio.sleep(0.1)


async def check_titles(sub):
    for post in sub.stream.submissions(pause_after=1):
        if post is None:
            break
        await title_search(post)
        await asyncio.sleep(0.1)


async def title_search(post):
    title = post.title
    id = post.id
    duplicate = is_duplicate('title', title)
    if duplicate:
        return False
    answer = find_iron_fist(type=post, text=title, id=id)
    print(f'\nANSWER:\n {answer}')


def is_title_duplicate(title):
    exists = os.path.exists(duplicate_titles)
    if not exists:
        return False

    with open(duplicate_titles, 'r') as commented:
        commented = commented.read().split(',')
        for othertitle in commented:
            othertitle = othertitle.strip()
            if othertitle == title:
                return True

    return False


async def comment_search(comment):

    text = comment.body
    # CHECKS:
    # Should not reply to yourself.
    yourself = True if comment.author == my_username else False
    if yourself:
        return False

    # Should not reply twice.
    duplicate = is_comment_duplicate(comment.id)
    if duplicate:
        return False

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
    save_duplicate_comment(comment.id)
    if not all_matches or len(all_matches) >= 3:
        print('not all_matches or len(all_matches>=3')
        print(all_matches)
        return False

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


async def find_iron_fist(**kwargs):
    thing = kwargs['type']
    text = kwargs['text']
    id = kwargs['id']

    # Get catch words that are in title.
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
    # All catch words should not be in title,
    # because bot should not correct when someone uses the whole catchphrase!
    save_duplicate(thing, id)
    if not all_matches or len(all_matches) >= 3:
        print('not all_matches or len(all_matches>=3')
        print(all_matches)
        return False

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

    return answer


def save_duplicate(thing, id):
    print(f"Saving {thing}:'{id}' as duplicate", end="")
    if thing in ['comment', 'c']:
        duplicate_file = duplicate_comments
    elif thing in ['post', 'title', 'p', 't']:
        duplicate_file = duplicate_titles
    else:
        print('not valid type')
        return False

    with open(duplicate_file, 'a+') as commented:
        print(" to file...")
        commented.write(id + ',')


def is_duplicate(thing, id):
    if thing in ['comment', 'c']:
        duplicate_file = duplicate_comments
    elif thing in ['post', 'title', 'p', 't']:
        duplicate_file = duplicate_titles
    else:
        print('not valid type')
        return False
    exists = os.path.exists(duplicate_file)
    if not exists:
        return False

    with open(duplicate_file, 'r') as commented:
        commented = commented.read().split(',')
        for otherid in commented:
            otherid = otherid.strip()
            if otherid == id:
                return True

    return False


def is_comment_duplicate(id):
    # if file containing duplicates doesn't exist:
    # its not a duplicate -> finish execution
    exists = os.path.exists(duplicate_comments)
    if not exists:
        return False

    with open(duplicate_comments, 'r') as commented:
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
        check_comments(marvelstudios),
        check_titles(defenders),
        check_titles(marvelstudios),
    )


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


asyncio.run(main())
