import os.path
import re

def save_as_duplicate(id):
    print(f"Saving id:'{id}' as duplicate",end="")
    with open('commented.txt','a+') as commented:
        print(" to file...")
        commented.write(id+'\n')


def check_if_duplicate(id):
    # if file containing duplicates doesn't exist:
    # its not a duplicate -> finish execution
    exists = os.path.exists('commented.txt')
    if not exists:
        return False
    
    with open('commented.txt','r') as commented:
        for otherid in commented:
            otherid = otherid.strip()
            if otherid==id:
                return True
    
    return False


def bold_quote(catch, quote):
    #p = re.compile(f'{catch}',re.IGNORECASE)
    bolded = f'**{catch}**'
    quote = re.sub(catch, bolded, quote)
    return quote
    

