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


Turns out I can use a regular expression after all. Huh

As the "first-match-wins" algorithm is identical to the "greedy"
   disambiguation method used by POSIX regular expressions, it is
   natural and commonplace to use a regular expression for parsing the
   potential five components of a URI reference.

   The following line is the regular expression for breaking-down a
   well-formed URI reference into its components.

      ^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?

Isn't the above a bit too lenient? It doesn't really test all that much and 
isn't good for our porpoises. So let's try something else:

http://www.faqs.org/rfcs/rfc3987.html


F*** it, let's setup my own validation just for this project (that could be swapped out later if needed).

For data:
[RFC2397](https://datatracker.ietf.org/doc/html/rfc2397)

data:[<mediatype>][;base64],<data>: ^data:(.*)(;base64)?,(.*)$
not doing any specific check for media type because reading [rfc6838](https://datatracker.ietf.org/doc/html/rfc6838) is one too many rfcs for today

viewsource: incorporated into http, https and file 

http and https: 

could always end up using (python validators library)[https://pypi.org/project/validators/]. Let's actually
do that. 

for files, this is gonna kinda suck so let's try and be a bit more strict (because there are a lot of edge cases that basically make a specific regex kinda silly)

viewsource gonna reuse the url validator 

for files, supporting linux and windows. REEEE ^file://(\/[\da-zA-Z\s\-_]+)+$ (linux) ^file://[a-zA-Z]:(\\[a-zA-Z\d\s\-_]+)+$ (windows)

eyyy we got ourselves a problem. That problem is:
- using the in built validators url validation is it fails self.assertTrue(url.validateURL('http://localhost:3000/'))
- so we need something else I guess. Blegh.

I'll copy some regex for now

The <mediatype> is an Internet media type specification (with
   optional parameters.) The appearance of ";base64" means that the data
   is encoded as base64. Without ";base64", the data (as a sequence of
   octets) is represented using ASCII encoding for octets inside the
   range of safe URL characters and using the standard %xx hex encoding
   of URLs for octets outside that range.  If <mediatype> is omitted, it
   defaults to text/plain;charset=US-ASCII.  As a shorthand,
   "text/plain" can be omitted but the charset parameter supplied.

TODO LATER: https://developer.mozilla.org/en-US/docs/Web/URI/Schemes/data 

"If the data is textual, you can embed the text (using the appropriate entities or escapes based on the enclosing document's type). Otherwise, you can specify base64 to embed base64-encoded binary data. You can find more info on MIME types here and here."

I am not done with all these exercizes yet but I want to read on a little to get a better idea of what will be required later (especially regarding the Data URLs part).

# Chapter 2

NBNBNB: sudo apt-get install python3-tk  was needed to install tkinter (not provided by pip)

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

" Although many URI schemes are named after protocols, this does not imply that use of these URIs will result in access to the resource via the named protocol."

That is very interesting. 
