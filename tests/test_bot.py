import bot.bot as bot
import pytest
import asyncio
import re

# runs only once before testing


@pytest.fixture(scope="module")
def vars():
    test_phrases_positive = {
        'iron_fist': ["iron fist", "IRON FIST", "iron fist"],
        'danny': ["danny", "Danny"],
        'protector': ["protector of kunlun", "protector of Kunlun", "protector of Kun-lun", "protector of K'un-lun"],
        'sworn_enemy_of_the_hand': ["sworn enemy of the hand"],
    }
    test_phrases_negative = {
        'empty': ['', ' '],
        'unrelated': ['dslkjaldkajs', ' I am talking about shit I dont want to talk about'],
        'quotes': ['> IRON FIST DANNY RAND SWORN ENEMY\n\nHere i am not talking about our lord',
                   'quote in the middl\n\n> iron fist\n\nthentalking more',
                   'quote at the\n\n> iron fist'
                   ]
    }
    return {'positive': test_phrases_positive, 'negative': test_phrases_negative}

# TEST FUNCTIONS


@pytest.mark.asyncio
async def test_finding_iron_fist(vars):
    test_phrases_positive = vars['positive']
    for phrase_list in test_phrases_positive.values():
        for phrase in phrase_list:
            print('asserting positive')
            result = await bot.find_iron_fist(text=phrase, id='1', type='c')
            print(f'phrase: {phrase}\n_________________________')
            assert result

    test_phrases_negative = vars['negative']
    for phrase_list in test_phrases_negative.values():
        for phrase in phrase_list:
            print('asserting negative')
            phrase = bot.delete_quotes(phrase)
            result = await bot.find_iron_fist(text=phrase, id='1', type='c')
            print(f'phrase: {phrase}')
            assert not result


def test_quotes():
    print('testing')
    quotes = ["> qutoes \n\n yolo",
              "quote in the middl\n\n> of  talking\n\nthentalking more", "quote at the\n\n> end"]
    for quote in quotes:
        result = bot.delete_quotes(quote)
        assert not has_quotes(result)


# HELPER FUNCTIONS

def has_quotes(text):
    pattern = re.compile(r'(>.*\n)|(>.+$)|(>.+\n)')
    return True if re.search(pattern, text) else False
