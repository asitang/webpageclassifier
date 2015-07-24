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


from bs4 import BeautifulSoup
import re
import math
import urllib.request


#reads the golden files and adds different versions of the same word and returns a list: like NEWS, news, News

def readgolden(filepath):
	inputfile=open(filepath,'r',encoding='cp1252', errors='ignore')
	goldenlist=[]
	for line in inputfile:
		line=line.rstrip('\n')
		goldenlist.append(line.lower())
		goldenlist.append(line.upper())
		goldenlist.append(line.title())
	return goldenlist	


#creates n grams for a string and outputs it as a list
def ngrams(input, n):
  input = input.split(' ')
  output = []
  for i in range(len(input)-n+1):
    output.append(input[i:i+n])
  return output

#checks for the existence of a set of words (provided as a list) in the url
def checkforwordinurl(url,wordlist):
	for word in wordlist:
		if word in url:
			return True
	return False	

# extracts all the values of a specific attribute of some specific tags (a list of tags) from an html page
def extractallclassnames(taglist,attrib,html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	classlist=[]
	for tag in taglist:
		for classtags in soup.find_all(tag):
			classlist.append(classtags.get(attrib))
	return classlist		

def extractallfromtag(taglist,html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	contentlist=[]
	for tag in taglist:
		for content in soup.find_all(tag):
			contentlist.append(str(content))
	return contentlist		


"""def numberoftags(taglist,html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	count=0
	for tag in taglist:
		for classtags in soup.findall(tag):
				count+=1"""




# finds the normalized cosine overlap between two texts given as lists
def cosinesimilaritymeasure(words,goldwords):
	wordfreq=dict()
	goldwordfreq=dict()
	commonwords=[]
	cosinesum=0
	sumgoldwords=0
	sumwords=0


	for goldword in goldwords:
		if goldword in goldwordfreq.keys():
			goldwordfreq[goldword]=goldwordfreq[goldword]+1
		else:
			goldwordfreq[goldword]=1

	for word in words:
		if word in wordfreq.keys():
			wordfreq[word]=wordfreq[word]+1
		else:
			wordfreq[word]=1	


	for word in goldwords:
		if word in wordfreq.keys():
			if word in goldwordfreq.keys():
				commonwords.append(word)
				cosinesum+=goldwordfreq[word]*wordfreq[word]

	for word in goldwords:
		sumgoldwords+=goldwordfreq[word]*goldwordfreq[word]
	
	for word in commonwords:
		sumwords+=wordfreq[word]*wordfreq[word]
	
	#print(commonwords)

	sumwords=math.sqrt(sumwords)
	sumgoldwords=math.sqrt(sumgoldwords)
	if sumgoldwords!=0 and sumwords!=0:
		return cosinesum/(sumwords*sumgoldwords)	
	return 0	
				


# This function categorizes and returns the urls as one of the following: 'blog', 'wiki', 'news', 'forum', 'classified', 'shopping' and 'undecided'
#
# THE BIG IDEA: It is inherently confusing to classify pages as clasifieds, blogs, forums because of no single or clear definition.
# Even if there is a definition the structure of the webpage can be anything and still comply with that definition.
# The flow is very important for the categorization.
#
# URL CHECK: The code checks the urls for WIKI, BLOGS, FORUMS and NEWS before anythin else. In case we have multiple clues in a single url
# such as www.**newsforum**.com, it gives utmost precedence to the wiki. Then treats the others as equal and keeps the result undecided hoping it will be 
# decided by one of the successive processes. 
# 
# WIKI: The easiest and most certain way of identifying a wiki is looking into its url.
#
# BLOG: these mostly have a blog provider: And in most cases the name gets appended in the blog url itself.
#
# FORUM: Although they come in different structure and flavors, One of the most common and exact way of recognizing them is thru their	
#			1. url: It may contain the word forum (not always true)
#			2. html tags: the <table>, <tr>, <td> tags contains the "class" attribute that has some of the commonly repeting names like: views, posts, thread etc.
#			The code not only looks for these exact words but also looks if these words are a part of the name of any class in these tags.
#
# NEWS: Checking the <nav>, <header> and <footer> tags' data (attributes, text, sub tags etc.) for common words we find in a news
#		website like 'world', 'political', 'arts' etc ... 'news' as well and calculates the similary and uses it with a threshhold.
#
# CLASSIFIED and SHOPPING: Here the code uses a two stage approch to first classify the page into one of these using a list of words for each.
#						 The main difference assumed was that a 'classified' page had many "touting" words, because it's people selling stuff,
#						 whereas a 'shopping' page had different kinds of selling words (ofcourse there is some overlap, the the code takes care of that)
#						 Then it checks see if the predicted type is independently relevent as a classified of shopping web page (using a threshhold).				
#						 The flow of how the sites are checked here is very important because of the heirarchy on the 
#						 internet (say a forum can be a shopping forum - 
#						 the code will correctly classify it as a forum)		
#	 
# The code uses some necessary conditions (if you may say) to find the accurate classification.
# Checking the url, header and 
# footer is also a very good	idea, but it may lead you astray if used even before using the above mentioned accurate techniques. Especially the 
# words in the header and footer may lead you astray (say a footer may contain both 'blog' and 'forum')	
# If indecisive this code will call the Hyperian Grey team categorizer (That code is commented -- please also import their code first)

def categorizeurl(url):
	url_type='undecided'
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as response:
		html_content = response.read()

	#check for blog providers name in the url
	
	blogproviderslist=readgolden('blog.txt')
	
	if checkforwordinurl(url,blogproviderslist):
			return 'blog'
		

	#check for 'wiki' word in the url: high precedence

	if 'wiki' in url:
		return 'wiki'

	#check for 'forum', 'news' or 'blog' in the url: equal precedence
	ct=0

	if 'forum' in url:
		url_type='forum'
		ct+=1

	if 'blog' in url:
		url_type='blog'
		ct+=1

	if 'news' in url:
		url_type='news'
		ct+=1

	if ct>1:
		url_type='undecided'
	elif ct==1:
		return url_type	
			

	#check if it's a forum: by cosine similarity on the 'class' attribute of <tr>, <td> and <table> tags

	forumclassnamelist=readgolden('forum.txt')

	

	tags=['tr','td','table']	
	classlist=extractallclassnames(tags,'class',html_content)
	tags=['nav','header','footer']
	contentlist=extractallfromtag(tags,html_content)

	#remove the NoneType
	classlist = [i for i in classlist if i is not None]
	#flatten a list of list
	classlist=[item for sublist in classlist for item in sublist]
	#check if the classnames contain any of the words from the 'forum' list
	classlist=[j for i in classlist for j in forumclassnamelist if j in i]	

	forumscore=cosinesimilaritymeasure(classlist,forumclassnamelist)
	#print('forum score::'+ str(forumscore))
	if forumscore>=0.4:
		return 'forum'


	#check if a news website: check the nav, header and footer data (all content, class and tags within), use similarity

	newslist=readgolden('news.txt')

	contentlist=' '.join(contentlist)
	contentlist=re.sub('[^A-Za-z0-9]+',' ', contentlist)
	contentlist=contentlist.split(' ')
	newsscore=cosinesimilaritymeasure(contentlist,newslist)
	#print('news score::'+ str(newsscore))
	if newsscore>0.4:
		return 'news'
		

	#check if a classified or shopping website

	shoppinglist=readgolden('shopping.txt')
	classifiedlist=readgolden('classified.txt')

	html_content=re.sub('[^A-Za-z0-9]+',' ', str(html_content))
	html_content=str(html_content).split(' ')+[' '.join(x) for x in ngrams(str(html_content), 2)]
	

	classifiedscore=cosinesimilaritymeasure(html_content,classifiedlist)
	shoppingscore=cosinesimilaritymeasure(html_content,shoppinglist)
	#print('classified score::'+ str(classifiedscore))
	#print('shopping score::'+ str(shoppingscore))
	if classifiedscore>shoppingscore:
		if classifiedscore>0.4:
			return 'classified'
	if shoppingscore>classifiedscore:
		if shoppingscore>0.4:
			return 'shopping'
	
	



	#call hyperian grey classifier if indecisive
	
	#if url_type=='undecided':
		#fs = DumbCategorize(url)
		#category=fs.categorize()
		#url_type=category
	    #return url_type
	
	return url_type


if __name__ == "__main__":
   
	url="http://www.npr.org/sections/health-shots/2015/07/16/423261565/webcast-sports-and-health-in-america"
	print(categorizeurl(url))


