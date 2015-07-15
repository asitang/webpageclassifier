# webpageclassifier

categorize a url using this: The flow is very important for the categorization:
THE BIG IDEA: It is inherently confusing to classify pages as clasifieds, blogs, forums because of no single or clear definition.
Even if there is a definition the structure of the webpage can be anything asd still comply with that definition.
BLOGS: these mostly have a bolg provider: And in most cases the name gets appended in the blog url itself.
FORUMS: Although they come in different structure and flavors, One of the most common and exact way of recognizing them is thru their	
			1. url: It cmay ontain the word forum (not always true)
			2. html tags: the <table>, <tr>, <td> tags contains the "class" attribute that has some of the commonly repeting names like: views, posts, thread etc.
			The code not only looks for these exact words but also looks if these words are a part of the name of any class in these tags.
 CLASSIFIEDS and SHOPS: Here I used a two stage approch to first classify the page into one of these using a list of words for each.
						 The main difference I assumed was that a 'classified' page had many "touting" words, because it's people selling stuff,
						 whereas a 'shopping' page had different kinds of selling words (ofcourse there is some overlap, the the code takes care of that)
						 Then I see if the predicted type is independently relevent as a classified of shopping web page (using a threshhold).				
		the flow of how the sites are checked here is very important because of the heirarchy on the internet (say a forum can be a shopping forum - 
		the code will correctly classify it as a forum)		
	 
		The code uses some necessary conditions (if you may say) to find the accurate classification.
		Checking the url, header and 
		footer is also a very good	idea, but it may lead you astray if used even before using the above mentioned accurate techniques. Especially the 
		words in the header and footer may lead you astray (say a footer may contain both 'blog' and 'forum')	
		If indecisive this code will call the hyperian grey team categorizer (That code is commented -- please also import their code first)
