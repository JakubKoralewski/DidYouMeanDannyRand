import os.path

def save_as_duplicate(id):
    print(f"Saving id:'{id}' as duplicate",end="")
    with open('commented.txt','a+') as commented:
        print(" to file...")
        commented.write(id+'\n')


def check_if_duplicate(id):

    # if file doesn't exist:
    # its not a duplicate -> finish execution
    exists = os.path.exists('commented.txt')
    if not exists:
        return False
    
    with open('commented.txt','r') as commented:
        for otherid in commented:
            if otherid==id:
                return True

