# webpageclassifier.py

import math
import re
import urllib.request

from bs4 import BeautifulSoup

"""
Copyright [2015] [jpl]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

__author__ = 'Asitang Mishra jpl memex'



def read_golden(filepath):
    """Reads a golden file and creates canonical (lowercase) versions of each word.
    Returns a list
    """
    goldenlist = []
    with open(filepath, 'r', encoding='cp1252', errors='ignore') as f:
        goldenlist = [x.lower().strip() for x in f.readlines()]
    print('Golden(%s):' % filepath, goldenlist)
    return goldenlist

# creates n grams for a string and outputs it as a list
def ngrams(input, n):
    input = input.split(' ')
    output = []
    for i in range(len(input) - n + 1):
        output.append(input[i:i + n])
    return output


# checks for the existence of a set of words (provided as a list) in the url
def word_in_url(url, wordlist):
    for word in wordlist:
        if word in url:
            return True
    return False


# extracts all the values of a specific attribute of some specific tags (a list of tags) from an html page
def extract_all_classnames(taglist, attrib, html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    classlist = []
    for tag in taglist:
        for classtags in soup.find_all(tag):
            classlist.append(classtags.get(attrib))
    return classlist


def extract_all_fromtag(taglist, html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    contentlist = []
    for tag in taglist:
        for content in soup.find_all(tag):
            contentlist.append(str(content))
    return contentlist


# def numberoftags(taglist,html_doc):
# 	soup = BeautifulSoup(html_doc, 'html.parser')
# 	count=0
# 	for tag in taglist:
# 		for classtags in soup.findall(tag):
# 				count+=1"""


def cosine_sim(words, goldwords):
    """Finds the normalized cosine overlap between two texts given as lists.
    """
    # TODO: Speed up the loops? If profile suggests this is taking any time.
    wordfreq = dict()
    goldwordfreq = dict()
    commonwords = []
    cosinesum = 0
    sumgoldwords = 0
    sumwords = 0

    for goldword in goldwords:
        if goldword in goldwordfreq.keys():
            goldwordfreq[goldword] = goldwordfreq[goldword] + 1
        else:
            goldwordfreq[goldword] = 1

    for word in words:
        if word in wordfreq.keys():
            wordfreq[word] = wordfreq[word] + 1
        else:
            wordfreq[word] = 1

    for word in goldwords:
        if word in wordfreq.keys():
            if word in goldwordfreq.keys():
                commonwords.append(word)
                cosinesum += goldwordfreq[word] * wordfreq[word]

    for word in goldwords:
        sumgoldwords += goldwordfreq[word] * goldwordfreq[word]

    for word in commonwords:
        sumwords += wordfreq[word] * wordfreq[word]

    # print(commonwords)

    sumwords = math.sqrt(sumwords)
    sumgoldwords = math.sqrt(sumgoldwords)
    if sumgoldwords != 0 and sumwords != 0:
        return cosinesum / (sumwords * sumgoldwords)
    return 0


def name_in_url(url):
    """Check for 'wiki', 'forum', 'news' or 'blog' in the url.
    'wiki' trumps, the rest must be unaccompanied by others.
    """
    count = 0
    if 'wiki' in url:
        return 'wiki'

    for word in ['forum', 'blog', 'news']:
        if word in url:
            url_type = word
            count += 1
    if count != 1:
        url_type = 'undecided'
    return url_type


def forum_score(html, forum_classname_list):
    """Return cosine similarity between the forum_classname_list and
    the 'class' attribute of <tr>, <td> and <table> tags.
    """
    tags = ['tr', 'td', 'table']
    classlist = extract_all_classnames(tags, 'class', html)

    # Flatten and remove the NoneType
    classlist = [i for i in classlist if i is not None]
    # flatten a list of list
    classlist = [item for sublist in classlist for item in sublist]
    print('\tforum classlist1:', classlist)
    # check if the classnames contain any of the words from the 'forum' list
    classlist = [j for i in classlist for j in forum_classname_list if j in i]
    print('\tforum classlist2:', classlist)

    score = cosine_sim(classlist, forum_classname_list)
    print('\tforum score: %4.2fs\n' % score)
    return score

def news_score(html, news_list):
    """Check if a news website: check the nav, header and footer data
    (all content, class and tags within), use similarity
    """
    tags = ['nav', 'header', 'footer']
    contentlist = extract_all_fromtag(tags, html)
    contentlist = ' '.join(contentlist)
    contentlist = re.sub('[^A-Za-z0-9]+', ' ', contentlist)
    print('\tnews contentlist:', contentlist)
    contentlist = contentlist.split(' ')
    score = cosine_sim(contentlist, news_list)
    print('\tnews score: %4.2f' % score)
    return score



def categorize_url(url, goldwords):
    """Categorizes urls as blog|wiki|news|forum|classified|shopping|undecided.

    THE BIG IDEA: It is inherently confusing to classify pages as clasifieds, blogs,
    forums because of no single or clear definition. Even if there is a definition
    the structure of the webpage can be anything and still comply with that definition.
    The flow is very important for the categorization.

    URL CHECK: The code checks the urls for WIKI, BLOGS, FORUMS and NEWS before anything
    else. In case we have multiple clues in a single url such as www.**newsforum**.com,
    it gives utmost precedence to the wiki. Then treats the others as equal and keeps
    the result undecided hoping it will be decided by one of the successive processes.

    WIKI: The easiest and most certain way of identifying a wiki is looking into its url.

    BLOG: these mostly have a blog provider: And in most cases the name gets appended in the blog url itself.

    FORUM: Although they come in different structure and flavors, one of the most
    common and exact way of recognizing them is thru their:
        1. url: It may contain the word forum (not always true)
        2. html tags: the <table>, <tr>, <td> tags contains the "class" attribute that
           has some of the commonly repeting names like: views, posts, thread etc.
           The code not only looks for these exact words but also looks if these words
           are a part of the name of any class in these tags.

    NEWS: Checking the <nav>, <header> and <footer> tags' data (attributes, text, sub tags
    etc.) for common words we find in a news website like 'world', 'political', 'arts' etc
    ... 'news' as well and calculates the similary and uses it with a threshhold.

    CLASSIFIED and SHOPPING: Here the code uses a two stage approch to first classify the
    page into one of these using a list of words for each. The main difference assumed was
    that a 'classified' page had many "touting" words, because it's people selling stuff,
    whereas a 'shopping' page had different kinds of selling words (of course there is some
    overlap, the the code takes care of that). Then it checks see if the predicted type is
    independently relevent as a classified of shopping web page (using a threshhold).

    The flow of how the sites are checked here is very important because of the heirarchy
    on the internet (say a forum can be a shopping forum - the code will correctly classify
    it as a forum)

    The code uses some necessary conditions (if you may say) to find the accurate classification.
    Checking the url, header and footer is also a very good	idea, but it may lead you astray
    if used even before using the above mentioned accurate techniques. Especially the
    words in the header and footer may lead you astray (say a footer may contain both 'blog'
    and 'forum')

    If indecisive this code will call the Hyperion Gray team categorizer
    (That code is commented -- please also import their code first)

    """
    hdr = {'User-Agent': 'MEMEX Page Classifier'}
    req = urllib.request.Request(url, headers=hdr)
    # TODO: fails on sites requiring cookies
    # Either add HTTPCookieProcessor, or use requests (for humans)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8', 'backslashreplace').lower()

    # 1. Check for blog goldwords
    if word_in_url(url, goldwords['blog']):
        return 'blog'

    # 2. Check for category name in URL
    name_type = name_in_url(url)
    if name_type != 'undecided':
        return name_type

    # 3. Check if cosine similarity suggest a forum
    if forum_score(html, goldwords['forum']) >= 0.4:
        return 'forum'

    # 4. Check if cosine similarity suggests news
    if news_score(html, goldwords['news']) >= 0.4:
        return 'news'

    # 5. Check if cosine similarity suggests shopping or classified.
    # TODO: Should we be using Sets?
    text = re.sub(u'[^A-Za-z0-9]+', ' ', html)
    print('\t#5 text:', text)
    text_list = text.split(' ') + [' '.join(x) for x in ngrams(text, 2)]
    classified_score = cosine_sim(html, goldwords['classified'])
    shopping_score = cosine_sim(html, goldwords['shopping'])
    print('\tclassified score:: %4.2f' % classified_score)
    print('\tshopping score:: %4.2f' % shopping_score)
    if 0.4 < classified_score > shopping_score:
        return 'classified'
    if 0.4 < shopping_score > classifiedscore:
        return 'shopping'


        # call hyperian grey classifier if indecisive

        # if url_type=='undecided':
        # fs = DumbCategorize(url)
        # category=fs.categorize()
        # url_type=category
        # return url_type
    return 'undecided'

def expand_url(url):
    if url.startswith('http'):
        return url
    else:
        return('http://' + url)


def get_goldwords():
    gold_words = {}
    for name in ['blog', 'forum', 'news', 'shopping', 'classified']:
        gold_words[name] = read_golden(name + '.txt')
    return gold_words

if __name__ == "__main__":
    import pandas as pd
    gold_words = get_goldwords()
    with open('urls.csv') as f:
        df = pd.read_csv(f, header=0, skipinitialspace=True)
    for url in df['URL']:
        print()
        print(url)
        eu = expand_url(url)
        print(eu)
        ans = categorize_url(eu, gold_words)
        print('\t---> %s <---' % ans)

    #df['Test'] = [categorize_url(expand_url(url)) for url in df['URL']]
    print(df)
