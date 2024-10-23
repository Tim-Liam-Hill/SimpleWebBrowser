# SimpleWebBrowser
A simple web browser built with the help of https://browser.engineering/index.html

# TODOS
* Setup a testing framework 
* setup documentation of classes/methods 
* Once done, re-write in C++ with better design patterns. 

# Exercises 1

we should have a list of standard headers we send through to make things 
easier to keep track of. 

We should have a list of accepted schemes we accept and switch some set of criteria based on them. add
- file 
- data 

question: how do we switch based on scheme? is a decorator worth here?
Probably not since there is noticable difference between how we handle each 
case. IE: not enough overlap to keep things generic.

Then a strategy design pattern could be better I suppose. Slight overkill maybe since [there aren't many schemes to support](https://developer.mozilla.org/en-US/docs/Web/URI/Schemes).


I can use a decorator for if we are decrypting data, but do we need that? simple 
if statement can actually just suffice.


I realize now that it might be a good idea to validate the input urls (URIs). The thing is,
this isn't actually as trivial as you might first think. 
[RFC3987](http://www.faqs.org/rfcs/rfc3987.html) gives the ABNF for IRIs but I think I will go with [RFC3986](http://www.faqs.org/rfcs/rfc3986.html)

The grammar is given in ABNF form so my options are either to write my own parser or to use one that already exists in python. I think I might just go for the latter now to avoid getting too bogged down. Plus: I have written parsers before and figure it would be good to see how other more mainstream parsers work. 

[PLY](https://www.dabeaz.com/ply/) seems like it could be a good choise since it seems to be based on Yacc.

STEPS:

- get the full grammar for a URI
- get it into YACC format
- get it to work with PLY
- implement error handling. 

"Each URI begins with a scheme name"

"The interpretation of a URI depends only on the characters used and not on how those characters are represented in a network protocol."

# QUESTIONS

1. The difference between URI, URN and URL (refer to RFCs)

Per [RFC 3305](http://www.faqs.org/rfcs/rfc3305.html), a URL is a 'useful but informal concept'. A URL is a URI with scheme http (or I imagine, https as well since that is likely what people would include).

[URI](http://www.faqs.org/rfcs/rfc3986.html) - a compact sequence of characters that identifies an abstract or physical resource
[URN](http://www.faqs.org/rfcs/rfc3305.html) - a URI that specifies the name of a resource specifically 
[URL](http://www.faqs.org/rfcs/rfc3305.html) - a URI that specifies the location of a resource specifically <- old definition, the def above (http) is now seemingly the contemporary view. 

According to [RFC 3986](http://www.faqs.org/rfcs/rfc3986.html):

"A URI can be further classified as a locator, a name, or both.  The
term "Uniform Resource Locator" (URL) refers to the subset of URIs
that, in addition to identifying a resource, provide a means of
locating the resource by describing its primary access mechanism
(e.g., its network "location").  The term "Uniform Resource Name"
(URN) has been used historically to refer to both URIs under the
"urn" scheme [RFC2141], which are required to remain globally unique
and persistent even when the resource ceases to exist or becomes
unavailable, and to any other URI with the properties of a name."

Further from this RFC:

" A common misunderstanding of URIs is that they are only used to refer
   to accessible resources.  The URI itself only provides
   identification; access to the resource is neither guaranteed nor
   implied by the presence of a URI.  Instead, any operation associated
   with a URI reference is defined by the protocol element, data format
   attribute, or natural language text in which it appears."

So in my mind, the URI only cares about identifying things. The subcategory of URL is more conscenred with the actual location as well (ie: ensuring that the identifier can actually be used to locate the resource). I guess an analogy could be:

- What is this strange substance you are talking about?
- Oh, it is <URI-NAME> Fine Wine!
- But I don't know where to find it
- If the <URL-NAME> is Steenberg Farm Fine Wine Subtype 13 then I know what it is and exactly where to find it!
