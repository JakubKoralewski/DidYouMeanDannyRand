import os
import praw


duplicate_comments = 'duplicate_comments.txt'
duplicate_titles = 'duplicate_titles.txt'


def save_duplicate(thing, id):
    print(f"Saving thing: {thing}, id: '{id}' as duplicate", end="")
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


def is_comment_duplicate(thing, id):
    if thing in ['comment', 'c'] or thing is praw.models.reddit.comment.Comment:
        duplicate_file = duplicate_comments
    elif thing in ['post', 'title', 'p', 't'] or thing is praw.models.reddit.submission.Submission:
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
