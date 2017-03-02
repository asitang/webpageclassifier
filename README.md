Categorizes urls as one of: blog|wiki|news|forum|classified|shopping|undecided.

**THE BIG IDEA:** It is inherently confusing to classify pages as clasifieds, blogs,
forums because of no single or clear definition. Even if there is a definition
the structure of the webpage can be anything and still comply with that definition.
The flow is very important for the categorization.

**URL CHECK:** The code checks the urls for WIKI, BLOGS, FORUMS and NEWS
before anything else. In case we have multiple clues in a single url
(such as www.**newsforum**.com), it remains undecided and continues to
successive processes, unless 'wiki' is present.

**WIKI:** Having 'wiki' in the url is considered to be diagnostic
(necessary and sufficient) for being a wiki.

**BLOG:** these mostly have a blog provider: And in most cases the name
gets appended in the blog url itself.

**FORUM:** Although they come in different structure and flavors,
these provide good clues:
    1. url: It may contain the word forum (not always true)
    2. html tags: Examine the class attribute for the
    `<table>`, `<tr>`, and `<td>` tags for commonly repeating names
    like: views, posts, thread etc. The code not only looks for these
    exact words but also looks if these words are a part of the name
    of any class in these tags.

**NEWS:** Checking the `<nav>`, `<header>` and `<footer>` tags' data
(attributes, text, sub tags etc.) for common words we find in a news
website like 'world', 'political', 'arts' etc... 'news' as well and
calculates the similary and uses it with a threshhold.

**CLASSIFIED** and **SHOPPING**: Here the code uses a two stage approach
to first classify the page into one of these using a list of words for each.
The main difference assumed was that a 'classified' page had many "touting"
words, because it's people selling stuff, whereas a 'shopping' page had
different kinds of selling words (of course there is some overlap, the
code takes care of that). Then it checks see if the predicted type is
independently relevent as a classified of shopping web page
(using a threshhold).

## Notes
The flow of how the sites are checked here is very important because
there is a hierarchy: a forum can be a shopping forum. This code will
correctly classify it as a forum.

The code uses some necessary conditions to find the accurate classification.
Checking the url, header and footer is also a very good	idea, but it may lead you astray
if used even before using the forementioned accurate techniques. Especially the
words in the header and footer may lead you astray (say a footer may contain both 'blog'
and 'forum')

If indecisive this code will call the Hyperion Gray team categorizer
(That code is commented -- please also import their code first)
