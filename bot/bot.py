import asyncio
import json
import os
import random
import re
import praw
import logging
import sys
from duplicate import is_comment_duplicate, save_duplicate, is_title_duplicate
for p in sys.path:
    print(p)

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

log_answer = lambda answer: logging.info(f'\n_______________________________________\nANSWER:\n {answer}\n_______________________________________')


async def check_comments(sub):
    logging.info(f'starting in: {sub}')
    for comment in sub.stream.comments(pause_after=0):
        if comment is None:
            logging.warning('comment is None')
            break
        logging.info(f'checking {sub}')

        text = comment.body
        id = comment.id
        yourself = True if comment.author == vars.my_username else False
        if yourself:
            logging.warning('yourself')
            continue

        # Should not reply twice.
        duplicate = is_comment_duplicate('comment', id)
        if duplicate:
            logging.warning('duplicate')
            continue

        # Delete quotes
        text = delete_quotes(text)

        answer = await find_iron_fist(type='c', text=text, id=id)
        if answer:
            log_answer(answer)
        else:
            logging.info('not found')
        await asyncio.sleep(0.1)


def delete_quotes(text):
    logging.info('deleting quotes')
    quotes = re.compile(r'(>.*\n)|(>.+$)|(>.+\n)')
    return re.sub(quotes, '', text)

async def check_titles(sub):
    logging.info('checking titles')
    for post in sub.stream.submissions(pause_after=1):
        if post is None:
            logging.warning('post is None')
            break
        await title_search(post)
        await asyncio.sleep(0.1)


async def title_search(post):
    logging.info('searching title')

    title = post.title
    id = post.id
    duplicate = is_comment_duplicate('title', title)
    if duplicate:
        return False
    answer = await find_iron_fist(type='post', text=title, id=id)
    if answer:
        log_answer(answer)
    else:
        logging.info('not found')

async def find_iron_fist(**kwargs):
    """ Find an Iron Fist reference in the given text.

        Args:
        thing (str): type of comment: 'comment', 'c' or title: 'p', 't', 'post', 'title'.
        text (str): the text to be searched.
        id (str): id to be fed to duplicate functions.

    """
    
    thing = kwargs['type']
    text = kwargs['text']
    id = kwargs['id']
    logging.info(f'find_iron_fist(type={thing}, text={text}, id={id}')

    # Get catch words that are in title.
    all_matches = []
    for catch in vars.catches:

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
        logging.info('not all_matches or len(all_matches>=3')
        logging.info(all_matches)
        return False

    logging.info(all_matches)
    logging.info('\n\n'+ text)

    for match in all_matches:
        catch = match[0]
        quote = match[1]
        ai_answer = f"Who is {quote.group(2)}?"

        # Get random answer.
        i = random.randint(0, len(vars.answers)-1)
        quote = bold_quote(catch, quote[0])
        await asyncio.sleep(0.01)

    answer = f"> {quote}\n\n{ai_answer} {vars.answers[i]}"

    return answer


def bold_quote(catch, quote):
    bolded = f'**{catch}**'
    quote = re.sub(catch, bolded, quote)
    return quote


def test_comments():
    with open('testcomments.txt', 'r') as c:
        comments = c.read().split(',')
    return comments


async def async_main():
    logging.info('starting async_main function')
    defenders = vars.reddit.subreddit("Defenders")
    marvelstudios = vars.reddit.subreddit("marvelstudios")

    await asyncio.gather(
        check_comments(defenders),
        check_comments(marvelstudios),
        check_titles(defenders),
        check_titles(marvelstudios),
    )


class vars():
    # Log in.
    reddit = praw.Reddit(user_agent=os.environ['USER_AGENT'],
                         client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'],
                         username=os.environ['REDDIT_USERNAME'], password=os.environ['REDDIT_PASSWORD'])

    my_username = reddit.user.me()
    logging.info(f"Logged in as {my_username}")

    # Get triggers, answers from JSON file
    # with open('quotes.json', 'r') as quotes:
    with open(os.path.join(os.path.dirname(__file__), 'quotes.json'), 'r') as quotes:
        logging.info(f'quotes.json opened successfully')
        quotes = json.load(quotes)
    
    # Things triggering bot:
    all_catches = quotes['catches']
    catches = all_catches['basic']
    catches_hi = all_catches['hi']

    # Answers for triggers:
    all_answers = quotes['answers']
    answers = all_answers['basic']
    answers_hi = all_answers['hi']


if __name__ == '__main__':
    logging.info('file opened locally')
    #from duplicate import save_duplicate, is_comment_duplicate, is_title_duplicate
    asyncio.run(async_main())
else:
    logging.info('file imported')
    #from bot.duplicate import save_duplicate, is_comment_duplicate, is_title_duplicate
