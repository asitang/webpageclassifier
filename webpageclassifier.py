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

__author__ = 'Asitang jpl memex'


from bs4 import BeautifulSoup
import re
import math
import urllib.request

#creates n grams for a string and outputs it as a list
def ngrams(input, n):
  input = input.split(' ')
  output = []
  for i in range(len(input)-n+1):
    output.append(input[i:i+n])
  return output

#checks for the existence of a word in the url
def checkforwordinurl(url,wordlist):
	for word in wordlist:
		if word in url:
			return True
		else:
			return False	

# extracts all the values of a specific attribute of some specific tags (a list of tags) from an html page
def extractallclassnames(taglist,attrib,html_doc):
	soup = BeautifulSoup(html_doc, 'html.parser')
	classlist=[]
	for tag in taglist:
		for classtags in soup.find_all(tag):
			classlist.append(classtags.get(attrib))
	return classlist		

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
	
	sumwords=math.sqrt(sumwords)
	sumgoldwords=math.sqrt(sumgoldwords)
	if sumgoldwords!=0 and sumwords!=0:
		return cosinesum/(sumwords*sumgoldwords)	
	return 0	
				


# categorize a url using this: The flow is very important for the categorization:
# THE BIG IDEA: It is inherently confusing to classify pages as clasifieds, blogs, forums because of no single or clear definition.
# Even if there is a definition the structure of the webpage can be anything asd still comply with that definition.
# BLOGS: these mostly have a bolg provider: And in most cases the name gets appended in the blog url itself.
# FORUMS: Although they come in different structure and flavors, One of the most common and exact way of recognizing them is thru their	
#			1. url: It cmay ontain the word forum (not always true)
#			2. html tags: the <table>, <tr>, <td> tags contains the "class" attribute that has some of the commonly repeting names like: views, posts, thread etc.
#			The code not only looks for these exact words but also looks if these words are a part of the name of any class in these tags.
# CLASSIFIEDS and SHOPS: Here I used a two stage approch to first classify the page into one of these using a list of words for each.
#						 The main difference I assumed was that a 'classified' page had many "touting" words, because it's people selling stuff,
#						 whereas a 'shopping' page had different kinds of selling words (ofcourse there is some overlap, the the code takes care of that)
#						 Then I see if the predicted type is independently relevent as a classified of shopping web page (using a threshhold).				
#		the flow of how the sites are checked here is very important because of the heirarchy on the internet (say a forum can be a shopping forum - 
#		the code will correctly classify it as a forum)		
#	 
#		The code uses some necessary conditions (if you may say) to find the accurate classification.
#		Checking the url, header and 
#		footer is also a very good	idea, but it may lead you astray if used even before using the above mentioned accurate techniques. Especially the 
#		words in the header and footer may lead you astray (say a footer may contain both 'blog' and 'forum')	
#		If indecisive this code will call the hyperian grey team categorizer (That code is commented -- please also import their code first)

def categorizeurl(url):
	url_type='undecided'
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as response:
		html_content = response.read()

	#check for blog providers name in the url
	blogproviderslist=[]
	blogproviders=open("blogs.txt",'r',encoding='cp1252', errors='ignore')

	for line in blogproviders:
		line=line.rstrip('\n')
		blogproviderslist.append(line)
		
	if checkforwordinurl(url,blogproviderslist):
			url_type='blog'
			return url_type
		

	#check for the word 'forum' in the url

	if 'forum' in url:
		url_type='forum'
		return url_type

	if 'blog' in url:
		url_type='blog'
		return url_type		

	#check if it's a forum: by cosine similarity on the 'class' attribute of <tr>, <td> and <table> tags

	forumclassnamelist=[]
	forumclassnames=open("forum.txt",'r',encoding='cp1252', errors='ignore')

	for line in forumclassnames:
		line=line.rstrip('\n')
		forumclassnamelist.append(line)

	

	tags=['tr','td','table']	
	classlist=extractallclassnames(tags,'class',html_content)
	#remove the NoneType
	classlist = [i for i in classlist if i is not None]
	#flatten a list of list
	classlist=[item for sublist in classlist for item in sublist]
	#check if the classnames contain any of the words from the 'forum' list
	classlist=[j for i in classlist for j in forumclassnamelist if j in i]	

	score=cosinesimilaritymeasure(classlist,forumclassnamelist)
	if score>=0.5:
		url_type='forum'
		return url_type

	#check if a classified or shopping website

	shoppinglist=[]
	shopping=open("shopping.txt",'r',encoding='cp1252', errors='ignore')
	classifiedlist=[]
	classified=open("classified.txt",'r',encoding='cp1252', errors='ignore')

	for line in shopping:
		line=line.rstrip('\n')
		shoppinglist.append(line)

	for line in classified:
		line=line.rstrip('\n')
		classifiedlist.append(line)	

	re.sub('[^A-Za-z0-9]+',' ', str(html_content))	
	html_content=str(html_content).split(' ')+[' '.join(x) for x in ngrams(str(html_content), 2)]
	

	classifiedscore=cosinesimilaritymeasure(html_content,classifiedlist)
	shoppingscore=cosinesimilaritymeasure(html_content,shoppinglist)

	if classifiedscore>shoppingscore:
		if classifiedscore>0.5:
			url_type='classified'
			return url_type
	if shoppingscore>classifiedscore:
		if shoppingscore>0.5:
			url_type='shopping'
			return url_type
					

	#call hyperian grey classifier if indecisive
	
	#if url_type=='undecided':
		#fs = DumbCategorize(url)
		#category=fs.categorize()
		#url_type=category
	    #return url_type
	
	return url_type


if __name__ == "__main__":
   
	url="https://forums.gentoo.org/"
	print(categorizeurl(url))


