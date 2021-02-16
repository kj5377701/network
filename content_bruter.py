from urllib.request import *
import threading
import queue
from urllib import parse


threads = 50
target_url = 'http://testphp.vulnweb.com'
woedlist_file = '/tmp/all.txt'
resume = None
user_agent = 'Mozilla/5.0'#????


def build_wordlist(wordlist_file):
    fd = open(wordlist_file, 'rb')
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print('resumeing wordlist from: %s' % resume)
        else:
            words.put(word)
    return words


def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []
        #check if attempt is a doc
        if '.' not in attempt:
            attempt_list.append('/%s/' % attempt)
        else:
            attempt_list.append('/%s' % attempt)

        if extensions:
            for extension in extensions:
                attempt_list.append('%s%s' % (attempt, extension))

        for brute in attempt_list:
            url = '%s%s' % (target_url, parse.quote(brute))
            try:
                headers = {}
                headers['User-Agent'] = user_agent
                r = Request(url)
                response = urlopen(r)

                if len(response.read()):
                    print('%d => %s' % (response.code, url))
            except:
                pass


word_queue = build_wordlist(woedlist_file)
extensions = ['.php', '.bak', '.orig', '.inc']

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions))
    t.start()
