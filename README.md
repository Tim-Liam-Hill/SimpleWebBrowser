# TODOs 

* TODO: create new Tag for Script elements and handle them differently. Use similar handling for pre and code tags 

# SimpleWebBrowser
A simple web browser built with the help of https://browser.engineering/index.html

# GOAL 

Developing a full web-browser capable of handling most modern websites is far beyond my abilities (at present, we will see again 20 years from now). The goal is instead to create a browser as given by the textbook I am following. Once I have that I will aim to have a browser that can browser using [FrogFind](http://frogfind.com/about.php) as its default search engine
- UPDATE: as of recently (18/11/2024) Frogfoot no longer seems accessible. Thankfully, [Wiby](https://wiby.me/) is also a good option (but will require more features implemented on my end it seems). 
With respect to CSS, I will be happy if I can support centered text, background colors and maybe just maybe some flex things (but we will see). 

There is a high chance that I restart this project from scratch at some point since: 

1. The finished example browser [here](https://github.com/browserengineering/book/tree/main/src) doesn't seem as fleshed out as I initially thought it might be, so to better support more features I may need better design patterns
2. Python is whack and lame, C++ is where it is it
3. I am a masochist

Some websites to support: 
* https://motherfuckingwebsite.com/
* https://dudeism.com/ordination-form/
* https://serenityos.org/happy/1st/
* https://endchan.org/ (or rather, some less degenerate imageboard websites)
* https://physicscourses.colorado.edu/phys3220/3220_fa97/3220_fa97.html
* https://nothings.org/

# Thoughts

Currently, I am about done with chapter 3 and thinking ahead to CSS and JS implementations. What may be a good idea is to extend my current text 'tags' array concept to css classes. I'll also make sure I have a better lexer for my html

# TODOS
* Setup a testing framework (done)
* Moar tests (difficult to do for some classes)
* setup documentation of classes/methods 
* Once done, re-write in C++ with better design patterns. (lol, probably won't)
* Horizontal scrolling
* scrolling for different platforms
* on browser resize, don't reset scroll amount but instead make it proportional to original scroll
* heading tags!!!!! REEEEEEEEEEE (just all the tags in general)
* Currently the browser runs the HTML parser twice on first startup (not the http request because that is cached) likely due to the first tkinter config event. Make sure this doesn't happen when we switch libraries.
* TODO: nice syntax highlighting for view source.

# WishList

* support some basic svg

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

IDEA!!!!
Make an HTTP Response class/object for use in the cache. We can use this likely 
(store things like headers n such). Is this overkill for this project? At this stage yes but for later maybe not

Good urls to test exercize 1:
- https://timhill.co.za
- https://pornhub.com (transfer-encoding chunked)
- https://wikipedia.org (content-encoding gzip)
- https://httpwg.org/specs/rfc9111.html#field.expires (this page contains the Expires header to test caching)

I am having some problems with transfer-encoding chunked. I can get the length of the first chunk, but when 
I read in that length next, I don't get the full chunk. REEEEEEE!!!!

https://raindev.io/blog/http-content-and-transfer-encoding/

"Both headers could be used together, in such a case the body is first compressed with the algorithm specified by Content-Encoding and then split into chunks." 
I think I now see my initial mistake.

For caching, [this](https://httpwg.org/specs/rfc9111.html#calculating.freshness.lifetime) is rather useful.

# Chapter 2

NBNBNB: sudo apt-get install python3-tk  was needed to install tkinter (not provided by pip)

#  Chapter3 Exercises 

How to do superscript?? I want to avoid including an extra variable in the lines array but I am not sure I can do this without that. Basically I need an offset from the baseline to handle superscript and subscript numbers. 

Honestly, there is almost certainly a design pattern here that would make things easier (maybe state or strategy??). Each tag has its own small changes it makes and it is difficult to classify those all under the same umbrella (that is to say, there are a lot of different variables at play but many tags only deal with a small subset of them). In any case, I may as well just get this done even if it isn't exactly perfect: learn from it and rework it later if I must. 

I guess what we can do is separate tags based on when they take affect:

* Some take affect only during font creation
* Some take affect only during word extraction/saving
* Some only take affect during laying out the word on the line
Maybe some actually take affect during more than one of these but I am yet to see such a tag.

IDEA: everytime we encounter an opening tag, add it to a set of the currently tracked tags. Any 
time we encounter a closing tag, remove the appropriate tag. Then, whenever an operation would need to take into account a specific tag, make that operation a function that takes in the tags. Bam, 
science

# Chapter4 

I want to do the HTML parsing a bit more accurately than what the textbook gives. As such, I am referring to the [HTML spec](https://html.spec.whatwg.org/multipage/parsing.html) for more info.

It will be a 2 pass algorithm (as usual):
* Lex into tokens 
* Parse into a tree 

I have taken a gander a bit later into the book and it seems that we won't be executing Javascript when it is encounter. So for now, I won't be [executing scripts that modify the page while it is being parsed](https://html.spec.whatwg.org/multipage/parsing.html#scripts-that-modify-the-page-as-it-is-being-parsed). What I might do is put scripts into a list and once everything is done, come back and run the bois. So a 2 parse algo?? 

Honestly, I think using the books approach with a bit more elaboration is good enough. What we can do is just extract tag attributes using a more specific DFA once we get to that part. 

# Chapter 5

Seems like a refactor is in order. Seems like layout is going into a Tree pattern as well, so we 
don't want to have all the member variables in this class that we have now (since then initing becomes real hard). What we can do is make a new class that holds css/styling properties and clone and pass it down to children as needed. We can move the widt into this class aswell. 

Let's read the chapter fully before writing any code (which is uncharateristic of me I know). 

Seems like the books naming conventions match (Safari)[https://webkit.org/blog/114/webcore-rendering-i-the-basics/] somewhat.

### TODO: test https://news.ycombinator.com/ at the end of this chapter, it should like somewhat alright.

So we got some problems. Our browser isn't throwing any errors, but the web page we are rendering doesn't look quite right. For starters, block elements don't seem to have blocks between them. Only gaps that appear between elements are as a result of my previous work with paragraphs. We also have a problem with our HTML parser: for https://browser.engineering we get the following when printing the tree:

``` 
<html>
 <html>
 <html>
 <html>
 <html>
 <html>
 <html>
 <html>
 <html>
   <body>
     <html>
       <head>
         <meta>
           <link>
           ...
```

What the hell is that??? 

I also need to rework how I am handling things like italics and bolding etc (ie: these properties need to pass down the tree). Undoubtably the next chapter has some things that might address this but still.

Oh, and text get's sorta cut off at the bottom of the browser. REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE.

So, here is what we should do:

1. Make sure the HTML parser works (since it seems there is an edge case that makes it break)
2. Get a better understanding of the DOM we are building 
3. Fix the issue with BlockLayout not having extra spaces (?) (this will solve the issue of bottom text being cut in half I believe)
4. Maybe even just rework the whole Layout file

I think my issue happens when I create Non-Block elements (things just seem to stop).
The issue is very likely due to my malformed HTML tree (at least for site https://browser.engineering/layout.html#size-and-position).

I shall get back to this tomorrow. 
Reminder:
- Fix HTMLParser
- get my recurse function back in since I accidentally yeeted it. 
- make sure non block bois work. 

--- the next day --- 

let's fix this boi. Minimal reproduction needed to cause the duplicate error is below. It seems 
like the error is related to self closing tags with explicit />. I think I can adjust the DFA slightly to handle this. Note that the same error occurs if a tag that is self closing doesn't explicitly self close. 

``` 
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
    </head>
    <body>        
    </body>
</html>
```

I don't think the DFA needs to change: it will produce tokens correctly regardless of whether a self closing tag uses /> or not. 

``` 
elif tag in SELF_CLOSING_TAGS:
```

That's the issue. My tag is ```'meta charset="utf-8" /'``` which obviously isn't recognized as a self closing tag. Simple fix: extract the tag name before comparison.

So, when using the lovely hub as a test website it seems like the svg tag can throw some curveballs. At some point it would be nice to be able 
to parse svg tags, but for now I will just parse the svg tag as having a bunch of text. That is to say: an svg tag will only have one child which is a text tag.
Later on I can work on how I want to parse this (since I imagine svg's have their own weird rules).

I fixed one bug but still have another on the hub. Honestly, my browser seems to work with a bunch of other sites so I am inclined to think this is due to the hub being an absolute mess of a website. [Github](https://github.com/aws/aws-sdk-js-v3/issues/6779) might be having issues as well for me. I am going to leave it for now so that I can make progress. 

# Chapter 6

Now we starting to do some cooking. 
So for the last chapter I already worked on a better system for parsing html and tag bodies. It seems like I won't need to necessarily replace that but I do need to consider how to incorporate what this chapter does into what I am doing.

On the brightside, once I have implemented this chapter, I can go back and download stylesheets to apply to pages. Yay! We can (and may have to) incorporate multithreading into the browser so that multiple resources can be downloaded in tandem. Yay! 

So this chapter builds a parser that takes in property value pairs. I will need one that can parse actual CSS files. I will almost certainly have to extend what is going on here. Update: I think that this actually does handle parsing full CSS files. I am going to read through the chapter fully once then come back to this. 

I may have to implement my own id selector (since that seems important).

So, we may need to rework our validation code inside of URL since now we are supporting relative urls :/. Actually, do we?? 

We can use the resolve function and then the request function afterwards? 
What we need is the base host and scheme. I suppose what we can do is return that with the content of our first request? If there are relative links then necessarily they relate to the main content right?? But what about when we make requests for other things? How do we keep track???
Sigh. 

Keep the event logic in the Browser class and call appropriate functions for the active page. 

* Page will store all the variables about the document (document height etc)
* Browser will store the info regarding the window (window height) and p

we need a window class

* Browser has a singular window which holds all the information about the space on which we can render
* Browser has multiple pages, each with their own unique scroll values, doc heights etc
* Each page has a reference to the window object which it uses to calculate its own values n shit
* Browser has the on resize listeners which it then uses to update tkinter
* the window class does NOT store the tkinter canvas and such, the browser does. Window just stores info about the space on which we render and handles rendering of things not unique to a page (eg: scroll bar thingy, search bar etc). 
* ACTUALLY, why shouldn't window store those things? I don't think its a bad idea actually.
* but then window needs to know about the active page.
* so then maybe window takes care of those things?
* but then window basically ends up taking over the role of browser.
* So I guess we don't need a window class after all. 
* But here is the thing: someone has to store data about the tkinter window (width height etc)
* This data needs to be made available to each and every page, without the page being in control of them (pages need this info to draw content)
* Thing is, are pages ever able to call their own draw function? If so, they need a reference that lets them access the window values. If not, then we can just pass down the values any time we do a render
* I think the latter will work. If there is a click on the screen that will be processed by the event handlers which will be defined in Browser (since we need to check if click on page content or navbar etc). Then, if needed, we can propagate that click down to the page and call the page's draw function once done with the window values
* This way no copies of data and stale data. 

KISS

Back a day later, lets refactor. 

* Page stores all data for a specific window
* Browser stores all the pages as well as active page and tkinter window
* Page can have a font cache that is available to all instances of page.

(reminder, I am at heading 5)

It is a good thing I read ahead sometimes: what I am doing is actually what ends up being done in the next chapter (with the same logic w.r.t separation of concerns it seems). With this in mind let's stop what I am doing now with this refactor and focus instead on completing this chapter.

Reverted, but now it seems like google.com is throwing errors. why? Seems like we have some legacy code: we shouldn't have a flush function any more since text belongs to text nodes. We need to implement functionality of 'br' and 'p' tags without flush 

So some more things are broken. Superscript isn't working which is annoying. Also not sure how to reimplement br elements. Reee.

Turns out the re-implementation for br was pretty simple. Now just need to figure out superscript (which should be doable).

# Exercizes 

4.6 is a bit much in my opinion/doesn't have a trivial algorithm to use. Consider the below html fragment:

```<b>bold<i>both</b>italic</i>```

Here, we can do what the textbook wants because the tags are balanced (in that for each opening tag there is a closing tag). If that isn't the case we can have an issue. Consider the below example:

```<a> <b> <c> meow </a> <c> meow <b>```

Here we would need to implicitly close tags up until the a tag,, then re-add those tags in the right order. If there is no matching open 'a' tag on the unfinished stack however, we will pop off 
all elements and encounter an error.

The current way my project has been deeling with this is to just to check the current size of the stack before popping off elements when encountering a closing tag. We only pop off if size > 1.
I want to better ensure that closing tags actually match opening tags which will mean a more sophisticated algorithm. Also to note: the below html is valid but crashes my parser if the 
check above is not in place.

```<html><head></head><body></body></head>```

The issue seems to be the lack of any text nodes.

We should also consider how to make sure there are not multiple body and head tags. 

The textbook has kept things simple by operating under the assumption that the html will generally be well formed and that has kept the implementation simple. To handle malformed html will 
require a slight re-work and more in depth algorithm. 

At some point I may likely need to just clean up a lot of the code I have written but that's okay. 

I finished ex 4.6 before 4.2, maybe I should have done them the other way around? not sure but anyway, handling these p and i as special cases is annoying and makes the code less elegant but 
whatever.

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
