
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
-> that was done. Nice. 

 *** a period of time passes *** 
We are back, and to get back into this we need to pick up slightly. For starters, let's fix some obvious bugs.

1. we aren't pathing correctly when reading the Default css file. IE: if you run the python command outside the director of Browser.py then the code will file to find the Default css file. (done)
2. Setup some better testing ???? TDD????????

I recently was introduced to a way of developing in which you write your unit tests first then have live reloading enabled while you write the code that satisfies the unit tests. In realtime you can see the result of the changes you make which I think is very rad and will help me be a better developer. I want to implement that into this project if I can. 

Basically, [this post](https://stackoverflow.com/questions/73776076/is-there-a-way-to-rerun-all-pytest-tests-when-a-file-is-saved) covers exactly what I want. Nice!! 

Somehow I feel like it is late for that (even though it isn't but eh). 

Next step: heading 4 because we currently aren't extracting href links. URL class will need to change a bit to validate links :/


The problem here is the books code assumes we have always saved the base url's scheme, host and port in the URL object and it uses that to construct relative urls. This should work for me but I feel like it could be bug prone: if you make a request to a different domain (eg: google to fetch a font) and then try resolve a relative link (maybe you are dynamically resolving a stylesheet?) then you would get the wrong relative link. I am going to pass in an additional param so that we always specify which url is the base for our. 

Wait, so what they have done is they create a new URL for each new url string. I seem to be doing something different where I have a URL 'manager' that is used for each URL. So, I can either change to be more like them or carry on my approach. I think I might adopt their approach. But it feels kinda stinky somehow, so instead let's keep my approach and refactor URL to stop using those member variables for path, host etc. 

Who doesn't love a good refactor? While we are at it, why are Text and Tag classes in the URL.py file? This seems like a weird place for them to be. 

View source is a thing we need to keep track of.

So that refactor wasn't too bad. Let's get the resolve functionality working and then fix some HTML parser issues. 

I also want to do multithreading for requesting all the additional resources but we will get to that. 

Let's fix a bug (or more) with the HTML parser. 

https://motherfuckingwebsite.com/

I should set up tests for my HTML parser and make sure it passes all of them. Move all the other static html files I have made into that to retain saved work.
Honestly, using the book's HTML parser kinda has made things more difficult for me now because of how I tried to extend it. It might be worthwhile refactoring the Parser sooner to fix all the bugs and get rid of the weird behaviour. 


HTML comments are ruining my code. May need to extend the DFA. 
What is interesting is that my code doesn't seem to fail with all html comments so this is likely an edge case

``` 
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    
    <!-- FOR THE CURIOUS: This site was made by @thebarrytone. Don't tell my mom. -->

</head>

<body>
    <div>asfasdfsdaf</div>
    <div>Meow</div>
</body>
</html>
```

The above code doesn't fail but it also doesn't render anything. Comments are definitely not being parsed correctly. What is likely happening is my code treats the comment as an opening bracket that never get's closed.
Done, not bad. 

But we still have some bugs. Trying http://frogfind.com/about.php and getting errors. The issue was kinda funny: the condition for whether to add an html tag would check whether the string 'html' appears in the contents of the tag we are about to add. The problem is: it should actually be checking whether or not the tag we are about to add IS the html tag and as a result, the below HTML would attempt to add the meta tag assuming we already had another tag on the stack (leading to an invalid index access):

```

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 2.0//EN">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<html>
...
```

Its funny: I am meant to be in chapter 6 but I find myself fixing chapter 5's bugs. I am okay with that I guess, the longer this project goes the more progress slows but in some ways that should be expected (especially since I want to do more than what the textbook's code does by default).

So now we have a problem: if we only apply the default browser css then pre get's formatted correctly, but if we apply the other css files then pre does not get formatted correctly. Why? 

Also interesting: if I create a new css file and give it the below contents, then we aren't seeing the expected results. There is a div with an inline style that should have a blue background but it isn't getting that. 

``` 
div {background-color: aqua;}
p {background-color: aqua;}
```
Actually nevermind: it does work and I am just confused because the colors didn't blend well. 

We will need a lot of testing for this. I might also rework the CSS system a bit. The biggest issue right now seems to be the descendant tag thingies.

What I think I will do is complete this chapter then come back and rework as necessary. A lot of the code can be reused but I think some better design patterns exist (or rather, for the things I want to implement I will need a more complex solution than the base cases the book provides). 

Since we are diverting from the book let's get down what we want to support.

The desire for this CSS 'engine' is for it to support basic styling elements. The list for now will be:

* tag, class, id selectors
* background colors
* text color
* font family and size 
* text position (center, left, right)
* border (Question: will we support border radius? would be cool to do this)
* padding
* margin
* display

Possible additions:

* a subset of flex 
* grid 
* z index
* tables (this isn't really css??)
* background images (this is ambitious)

I do want some element of layout control. That is to say: I think it would cool to display things not just on the right hand side but actually relative to each other. 

The thing about the above list is that we won't implement each thing fully. For example: for border there are a lot of things that can be implemented (dashed borders, double borders etc). Not all of those will be supported in all likelihood.

I need to understand CSS a bit better, I have forgotten Inline vs Block elements and the quirks between the two. 

I think I will rework CSSParser to work similarly to how I refactored the URL class. That is: you create 1 CSSParser object and use that to parse everything (not a new object for everything).

TODO: remember to get style tag contents. 

Alrighty, what to work on now? 
* Extract style from style tags 
* rework CSSParser
* Figure out why CSS not working when I load in external stylesheets. -> turns out it is working. I was expecting pre tags to still display gray but their color is being overridden by a different stylesheet and I need to parse hex colors to colors we can use. -> actually wait, no I don't think this was it 

When we do rework our css functionality we will have to remember to keep file order priority (since some files of lower priority may load faster than files of another priority).

I need to not get too ahead of myself: some css things will get implemented later it seems. Regardless, there seems to be an issue. Background colors should be showing correctly but aren't (unless there is inline styling). It might actually be that the websites I am choosing are bad examples though :/ (https://www.classicdosgames.com/ was one I just tried but this doesn't choose background color by tag). Implementing other selectors could be useful round about now. 

Eyy it does actually work: https://tjasink.com/games/bb/ uses a class selector for the body and this reflects in my browser. Yay!! 

The book deletes a whole bunch of things from earlier that are now no longer used but I cannot yet do that: I have to make sure I retain functionality. 

need to just go back and test small, big, abbr abd sup again. They should still work but it doesn't hurt to check

One thing I definitely want to do is make sure that I preserve the given formatting for p and pre tags since I am currently not doing that. It makes sites like [this](https://tjasink.com/games/bb/ ) look like a jumbled mess. 

Shouldn't we be inheriting background color??? 

test.html is not displaying as expected. I think it relates to the fact that background color is not being inherited and that inheritance isn't working quite as expected???

Think I got it: certain tags aren't passing inherited properties as they should. Maybe when a non-block element has children???  Yeah. I think we may need to extend our check for when to consider an element inline or block. Or maybe just handle background color differently??? Maybe I am getting bogged down in a weird edge case that shouldn't really be a thing. Regardless, I need to read up on Block Elements and such. 

The solution here is to pass in background color to the DrawText object and then create a rectangle on top of which the text appears (since creating text does not allow for a background in tkinter). This will likely need to change once we start using a different library. For now I may ignore, we will see

Interestingly enough, it seems like [background-color isn't inherited](https://developer.mozilla.org/en-US/docs/Web/CSS/background-color#formal_definition). 

Ideally for CSS would should have a list of regex/rules for what values can appear on the rhs of a given value. 

For now:
1. Refactor CSS parser to handle more cases of css. 
2. Get started on other exercises 
3. ID selector
4. borders (REMEMBER TO UPDATE WIDTHS!!)
5. padding and margin (REMEMBER TO UPDATE WIDTHS!)

6.1 -> done 
6.6 -> In Progress
The problem here is the css side of things (parsing, applying) works, but my block layout and inline layout aint printing how I want it to. REEEEEEEE. 

I think I need to re-examine how nodes pass x and y coordinates to one-another. How we know whether or not to start on the same line depends on the previous nodes display. we should maybe create a function that when called tells the next node where to continue (this could also be useful if we decide to implement some basic grid/flex).

Need to think about what happens to spans inside div? 
I think Tkinter is messing with me. I am not sure you can have two text blocks side by side :/  -> nope, it definitely does. The issue is me. 

Found the issue: I am drawing rects over content I previously drew. Background color of white was throwing me off
So my logic was right and I was confused. Fix: make sure we correct the starting x and ending x for the rects that surround text. (Should there even be these rects??)

So now when inline doesn't draw rects everything works, but we need to add the rects in the event there is a background color/border/etc. The plan is to make a list of rects when we flush lines and add this to the display list for a block layout

Bam. Did fix things, but now its also broken. When we have large passages of text we jump too far down. Hmmmmm...
So the issue isn't actually large text, its when we have large text (eg paragraph) that contains other tags. I believe this is because of how we are calculating height. Yeah, let's try and write out the flow then implement

So, how about:
* keep track of min cursor x 
* when flush, if background color we first append a draw rect (eventually we will add border info)
* we use min_cursor x as start and wherever last word finished as end
* cursor_y + y = start and height becomes height of line
* reset min_cursor_x after flush
* 2 different classes: blocklayout and inline layout.
* method to compute x, y and width (maybe height as well in the case of setting explicit height)
* height and width won't be member variables, they will be methods (maybe for some cases they will be member variables but all layouts will call the methods rather than access the variables directly.)
* also methods to compute cursor x and cursor y 
* method for getHeight()
* method for getStartNextContent (since your height and where the next text should start are not always the same)

what to do about layout props and handle open/close tags? Layout props I think we can get rid of tbh, and if that is the case then we won't need the handleOpen/Close tags (since they modify layout props). We can slot those into new functions and have finer granularity about when they are called. 

Maybe there is a design patten here I could use, but honestly inheritence is enough. [This](https://stackoverflow.com/questions/44576167/force-child-class-to-override-parents-methods) is a cool replacement for pure virtual methods.

Need to handle display: none and list-item because that would be beautiful.
List item can have an inheritable indent prop which will allow us to have correct indentation.

We need to have a default display option since not all tags will have a display prop (or can we just use Inline as a default?)

Hmm, let's back up a second. [This](https://html.spec.whatwg.org/multipage/dom.html#kinds-of-content) specifies 
the different type of HTML elements, should we not use this then use a strategy pattern for displaying 
based on layout?? That could be a good idea. we should perhaps also ensure that [these global attributes](https://html.spec.whatwg.org/multipage/dom.html#kinds-of-content) 
are present on all html elements (just for good measure).

Just because I was confused: [default layout value is inline](https://developer.mozilla.org/en-US/docs/Web/CSS/display#formal_definition).

After some consideration, I am not going to model all HTML elements per the spec: I think that will take things outside of the scope I am willing to do. If I really want to later I can rework it in but for now I will do things based on the display property. The nice part about this is that later on I can reuse display logic if I rework things. 

Good news! - my rework is confusing me and there will undoubtably be bugs. Yay!!! 
I think the issue is I am thinking about implementing padding, margin and such before I need to. I should get the basics to work then try and tackle those. Writing unit tests would also definitely help. 

I can replace the layoutprops I was using with inherited css props. Which I should do. Meow. Need to remember to propagate those somehow though...

Once I am done with this refactor I should make a method for extracting lengths/numbers etc for css props somehow. 

So now we just have to fix the bugs that have come about as a result of the refactor. Now would be a good time to write unit tests and use those to ensure we don't introduct more bugs later. 

Its the same issue I had last time when calculating the height for inline elephants! Because many elements within an inline block will be on the same line, we mustn't count those one's twice! we must only count the non-overlapping pieces.

There is probs a cool answer to this, but I guess the easiest way to do this is to get the minimum y value of the children and the max y_value + self.height of the children. The diff gives our height. 
But wait, didn't we already try this???? meow??? 

Something is still wrong with my logic. What is happening is each block layout is having double the height of that before it, which is just a tad problematic. 

So my logic with respect go getting the height of a block element was correct, the issue I had was the y start for inline elements. Still, this thing is a buggy mess but we are getting somewhere.

I need to some test cases. that is what I really need. Minimal reproductions of bugs to fix later. 

Someone please explain to me why superscript is still working even though when I comment out the code I put in for it there is literally no change?? I am confused. 

Also interesting: my text also gets cut off a bit on the right hand side. 

Hmm... I am tired and not really getting much done now. 

Fixed one or two small things now, moving onto the real issue of overlapping text when I render the https://browser.engineering site. Seems like the issue relates to BlockLayouts not getting the correct starting y position from parents. Yep, found a minimal reproduction.

FIXED IT BY THE GODS HE HAS DONE IT!!!!!!!!!! MEOWOWOWOWOWOOWWO.

Now the fun/interesting part starts. We need to beef up our CSS parsing engine and start implementing functions to turn em, % and px values into actual usable values

So we gots to think of what needs to be added to our css parser. ID and class selector definitely. Also worthwhile making sure our Descendant selector works.
Descendant selector is not getting parsed correctly. Going to refer back to textbook to see if I missed something, but either way I think it will get fixed in rework

For the CSS rework, I think I will add:
* ID selector
* Class selector
* GroupSelector
* CombinationSelector
* Universal selector

The first two are self explanatory. The third will be a collection of selectors for rules that could match one or more bois. I may need a fourth that will match only a specific combination though... so yeah, combination selector (basically the books ex 6-8). Also universal selector is needed.

One thing we could consider is moving to a map of rules as opposed to a list of rules. Linear lookup of matching rules for each element is fairly slow so performance can definitely be improved (I think the textbook mentioned bloom filters?).

I JUST REALIZED HOW I CAN IMPLEMENT LISTS PROPERLY OH MY WORD LOL. Literally just use descendant selectors. Wow, that is so cool. 
Borrow from https://chromium.googlesource.com/chromium/blink/+/master/Source/core/css/html.css.

I might have to think about how I handle priorities as I change things up...

So, if I want to parse CSS nicely I will have to look more at its specifications, and [damn if it aint lengthy](https://www.w3.org/TR/css/).

The simplest place to start is to separate css into the following:
* The selector portion (up till first {)
* everything in the body of a specific selector (between the {})
* inside the body, we process using 2 states: the property name and property value [see here](https://www.w3.org/TR/css-cascade-5/#intro)

so let's have a 2 step parsing approach: we first separate based on selectors and the set of rules making up the body of the selector (property name and value). Once we have finalized a specific body we can look at expanding the short hand properties and priority. We may need to look at priority on a per value level as opposed to per selector level, what does the book say?? 

So let's get this idea down for tag classes:

* We will have a separate map for each Selector type
* We can map from a selector value (eg: 'div' tag) immediately to the array of selectors that would accept this (in many cases)
* selector rules are basically just a set of simpler rules with adjusted priorities
* descendant selector we will use a different approach: probably simpler
* has selector: no clue just yet what we will do. We can potentially use a bloomfilter or just store a list of tags/classes/ids
* priorities will be stored as a pair of file priority then rule priority.

Before getting into that, I want to fix a guick bug with frogfind that suggests my rework still has some issues. The issue seems to relate to ```br``` and ```hr``` tags so it shouldn't be too difficult to fix. The former we can just adjust its getYStart, the latter can be done with css only but will need border margin and padding to be implemented. For now I suppose I can just do the same for it as for ```br```

I am making a br a block element because that feels most natural. 

Fun fact: a spelling mistake was the reason my descendant selector class was not working. Now that it is working I can re-implement bullet points. Yay!!

For bullet points, it seems like there is a specific 'list-item' display type. I suppose I can implement that. It would basically just be a small wrapper around a (or maybe literally just a block item that inserts content based on its level and adjusts content width?). The question here is do I want to implement another layout class? 

I have it the wrong way around, I think I will do what chrome does. Basically: we have ul and ol being block display but the children they create are list-display elements. List-display elements will function mostly like inline-display elements unless the previous/next was/is a list-display element, in which case it will function as block. Duplicated code I guess but it is what it is. I don't think I will use psuedo elements (maybe I should though).

Initially I thought to reconsider our approach with layout trees: I really should look at using [HTML elements](https://en.wikipedia.org/wiki/Document_Object_Model) like Text Nodes, Element Nodes, Attribute nodes etc. The existing layout code can stay and be used as a strategy pattern I suppose. -> after some thinking and review, I am already doing this. The books Element and Text classes are pretty much that.

TODO: implement width correctly (will be needed for margin/border etc)

side quest: we are having an error parsing the html for frogfind.com. Let's figure out why.
-> the issue is their html is malformed. Interesting... 
Thankfully we can still access the about page.

Time to make a DFA for the new parser. 

So we need to give rules priorities instead of the selectors. this is because we can have important rules that override other rules (and also rules that are more important even if their file ordering is less important.)

Let's do a little bit of reading. 

Thought: we don't have to specify a priority for every individual property value pair in a Selector class but we should include priorities when we add the values to a node (in case we override them later).  

Will use [this](https://www.smashingmagazine.com/2007/07/css-specificity-things-you-should-know/) article as basis for calculating priorities.

Eugh, there is something I didn't think about: nested selectors. Parsing those is doable but I don't really want to think about that right now. Definitely would be interesting to do it at some point: I think the simplest way to do it is to parse recursively then turn recursed rules into combined rules. Will add it to the wishlist/TODO list.

There are a lot of Combinators/pseudo classes and pseudo-elements that can be matched. I think I will implement them minimally and get back to them later if they are something I actually want to implement (eg: on hover for links).

Per [W3 Schools](https://learn.shayhowe.com/advanced-html-css/complex-selectors/#child-selectors) we need to allow for direct descendants. Hmmmm ........ We should also really make our Descendant Selector more optimal but that is already an exercise we will do later. 

I think the best way to handle this is recursively. 

* Base selectors (tag,id,class, universal)
* pseudo-class (base selector followed by single :)
* pseudo-element (base selector followed by double ::)
* attribute selectors (base selector followed by [])
* combinator selectors ()

Algorithm to work as follows: 
* We have our little DFA go through the string 
* we use this DFA to parse base selectors, pseudo-elements, pseudo-classes and attribute combinators
* we tally up the priority using an array [id count, class count,tag count]
* once we hit a space, we are in territory of the combinators so we parse that recursively
* anytime we come back from a recursive call, we are done and we tally up priorities accordingly
* for combinators with children, only the parent priority needs to be correct so that is pretty cool. We could even make that a method...  

Turns out [pseudo compound selectors are a thing](https://drafts.csswg.org/selectors/#compound). Not sure what I am going to do with this information, probably just focus on handling one level of pseudo elements (that is to say, if we come accross a value like 'div::before::marker' then we will just have a single pseudo elements with value 'before::marker').


## CSS SPECIFIC NOTES

Parsing css could be weird so for the cases I am not too sure about I'll just see what chrome does and try mimic that. 

```
div>div {...} -> this is a valid direct ancestor boi
```

IDEA: only base selectors have to store prio, the rest can just work their prio out based on their base selectors. Magnificent!!!

Ah, slight confusion: what will we do for prio of pseudo and attribute selectors??? I think I can rethink how they work.

The pseudo/attribute classes will basically always have a base class of sorts (so they will always belong to an ID or class selector etc). Treat these bois as the same level as class selectors I guess. 

Something that could be an issue is the following:
```
div > span, h1 {...}
```
In the above, how does the precedence work? I imagine it would be a list of 2 different selectors [Child, Tag], but mein code might not parse things like that. Mine would go the other way around (or throw an error I guess).

What we could do is use more states instead of recursion. That is to say: for each of the descendant-type selectors we have additional states that signify we are getting the 'chain of selectors' and that only ends if and when we hit a , (or come to the end). Then we can use an array as a stack to get everything in the right order. I guess this can work, it just makes things a tad more complex. We would need 2 arrs: one for any sequences and another for the current chain of descendants. 

Do we even need the additional states? I don't think so really. 

This is getting complicated. Meow. We may need an additional var to handle the sequence boi. 

```div[value='arg'].class::after#id:hover > span {background-color: brown;}```
To parse the above:
1. Extract the div attribute pair, make an attribute selector. Put this in the 'finish' arr
2. we see the . so we know we are in a sequence selector. Create it, put the attribute selector in the sequence selector (IE: take from the finish arr) and add sequence selector to finish arr. Transition to sequence selector state.
3. We parse the .class::after till we reach the #. We accept this as a pseudo element tag and add it to sequence selector 
4. Repeat above for id:hover
5. We just saw a space so we leave sequence selector state (leave it on the finish arr)
6. We see the space so we know that we will be in a descendant mode (we ensure that the selector is stripped beforehand). Don't create any tags just yet
7. We see the arrow, we know the type of descendant tag this is. Take top of finish arr, create the descendant tag using that push back onto finish arr. 
8. Consume whitespace till start of next rule 
9. Consume span, add it to the descendant tag 
10. Return. 

This is doable it seems. I think can actually just use a single array/stack var since descendants only ever deal with the last tag (we are guaranteed to have at least 1 non-multiselect type of tag on top of the stack in well formed css so we can preserve comma separated rules using a single stack, but I should check this). I will need to double check the logic of the various combinators (eg: which tag is ancestor and which is predecessor). 

This CSS parser will need a lot of test cases, thankfully we have a testing framework set up already. 

So here's the thing: we can either make our DFA verbose or we can keep it simple but have the function that uses the DFA be verbose. That is to say: if we have our states representing the descendant selector, those states also need to keep track of psuedo-elements, psuedo-class and attributes. This is true for all combinators and this ends up creating a fair few number of states (which is par for the course for DFA's I suppose). 

I think I will stick with this approach since 1. it is more theoretical and 2. I think its okay. 

[ # . > , " " ~ : + @

I think there is a way to simplyfy things actually. What is the solution you ask? Why, its use ANOTHER PARSER!!!!

Each combinator is basically going to be extracting 'base' tags and these base tags can have attributes, pseudo elements and pseudo classes. Why not bundle that into a new parser? this means that we only have to write the parsing states for 'base' tags once instead of for each combinator.

Sometimes it is difficult being so smart. Naming things is still hard, but that is difficult regardless of how smart you are. 

While we are at this, we can make a base class for all selectors to implement since that feels really obvious to do. 

We will need to think about how we handle multiple Pseudo Elements/Pseudo classes. They should each create a new selector as opposed to being nested inside one another (like an attribute would be). 

QUESTION: can pseudo classes have attributes? Seems like I need to read some documentation: https://drafts.csswg.org/selectors/#relative

I think I have a problem in my approach when looking at [this](https://drafts.csswg.org/selectors/#example-3e6d4159) example. I may need to handle multiple selector thingies in my SelectorParser class. ACTUALLY: I should be able to manage with my current approach. 

I should really read through the docs. 

We are not [implementing namespaces](https://drafts.csswg.org/selectors/#type-nmsp), that is out of scope. 

I may need to elaborate on the pseudo-class section to handle quotes within a bracket.

Okay, so the updates will be:
* allow for pseudo-class elephants to have quotes in a bracket
* explicitly handle sequence selectors first??? 

So reading the docs is always a good idea, I just found [the grammar](https://drafts.csswg.org/selectors/#grammar)! The docs also include [further info for parsing stylesheets](https://drafts.csswg.org/css-syntax-3/#css-parse-something-according-to-a-css-grammar).

So for time constraints and my own sanity, I dont think I will implement the full grammar above (at least, definitely not now. Maybe later I'll think about it). I already have a way of generating an SLR table from a grammar (because that was a project I have done before yay) but I am already spending a lot of time on this chapter and want to move on. 

So, I will restrict the CSS that I am willing to select. It shall look like the following:

* Any number of base classes ```div.class.class2#ID...```
* The base classes themselves can have any number of attributes eg: ```div[value="1"].class[meow][meowmeow].class2#ID```
* Pseudo classes will never be followed by a base element or attribute and can only be followed by pseudo elements 
* nothing can follow a pseudo element

But now we have a shmall problem: how are we going to end up applying the pseudo-element and pseudo-class styles? For now we could just make them not match by default. Otherwise we need to have a way of keeping track of these things in nodes and not reapplying stylesheet on every event on the canvas

"All pseudo-classes behave in this same kind of way. They target some bit of your document that is in a certain state, behaving as if you had added a class into your HTML. " -? [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Pseudo_classes_and_elements).

For a number of pseudo classes it is actually sufficient to apply them 'statically' when we first apply css rules. EG: :first-child. It is the [user-action pseudo-classes](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Pseudo_classes_and_elements#user-action_pseudo_classes) that really give hassle. 

So I suppose what we could do is catagorize our pseudo-classes by whether or not they are user actions. Then we can keep track of those separately and apply them needed. 

I am getting ahead of myself though. Let's get the parser working and advance till we stop using tkinter and change to the other rendering library. That is when it makes more sense to implement more CSS features. For now, Pseudo-elements and Pseudo-classes will never match. 

QUESTION: if we have ```div.class[attr][attr2]``` do the attributes apply to .class only or to the combined boi? I guess it doesn't really make a difference since all the attribute selectors will do is test the presence of the attributes, and this won't affect 

Imagine being the smartest person in the world (ie: me) and simultaenously being the stinkiest, silliest boi in existence (also me). THE ORDER DOESN'T MATTER MY CHILD!!! We don't have to worry to which base selector something applies, the matching of sub-components is NOT order dependent. THis makes things a whole lot easier for me. 

I think I will get rid of my selector Sequence and make my Base Selector fulfill the same role. This will make things a bit easier. 

IT IS TIME!! Long weekend which means I can smash out the rest of the things I want to do for chapter 6. This means:

* Finish selector parser
* Test new selectors
* Finish CSS parser
* Test CSS extraction and application
* Do exercises

So I do need to think about how I will implement the combinators. Not going to worry about efficiency right now, just want it to be correct. Once unit tests are up and running maybe I'll return when performance is needed. 

Gonna make prio tuples of length 4 just in case we want to explicitly put file order and inline style values in the prio.

So for base selectors, the order in which they actually appear in the linked list is reversed. That is to say, ```div.class#id``` would actually give a list like (ID) => (Class) => (Div). I think the same thing actually works here since when we get a node we will test first if it matches us, THEN we go up a level and test whether our parent matches the expected parent. 

I should probably try and avoid leaving rude comments in my code but then again, it is MY code.

Here is an interesting algorithm for the Selectors parser:

* We get everything that will be in a selector (ie: go until we hit space, >, ~, + or ,)
* we push new selectors onto a queue
* when we finish parsing OR when we hit a comma, we navigate the queue from right to left
* we expect a pattern of 'base' 'combinator' 'base' 'combinator' 'base' ie: there must be exactly 1 more base than combinator
* recursively do this: get one base. If beginning of array return it
* if there is combinator, make base to right its child and call func with different index to get parent (which will be a base in the base case)

does that make sense? No? Lemme do a diagram (on the off chance someone reads this or I need it later):

```
.class  span > #beans {}

.class  span > #beans {}

[Class, descendant, Tag, child, ID]
[Class, descendant, Tag, child, ID]
[Class, descendant, Tag, Child(parent=None,child=ID)]
[Class, Descendant(parent=None,child=Tag),Child(parent=None,child=ID)]
now the other way and add parents
[Descendant(parent=Class,child=Tag),Child(parent=None,child=ID)]
[Child(parent=Descendant(parent=Class,child=Tag),child=ID)]
Which is as expected per unit tests
```

Not even sure I need a crazy DFA for this -> actually I do, just to make sure I make the right combinator class and handle errors. 
----

6.4 -> In progress

Just started reading ahead and it seems like the rework I did for my HTML elements into Layout elements is similar to what the next chapter handles. Still, I like my solution and can actually incorporate a bit of the books solution into my own so yay!!

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
