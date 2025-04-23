
# Run steps

Its been a hot moment since I have worked on this project. This is leading me to realize how important documentation really is since I have forgotten what I was working on and how to run this project. TeeHee~

Browser is the main entry point. We run that file. As of chapter 6 the way of running is:

```
python3 Browser.py <url>
```

I know I will need a virtual environment in the future, so why not just set one up now??? 

```
python3 -m venv ./env
source ./env/bin/activate
deactivate
```

Not entirely sure if I have done things correctly :/ we will find out at some point I suppose. 
Why did I create the virtual environment in the root and not in the python folder????????

To run an individual module: ```python3 -m src.CSS.CSSParser``` (from the python directory)

# lessons learned

 * setting up testing before writing any code is a good idea
 * main branch should always have latest working code. Leave experiments and such for other branches
 * setup your dev environment BEFORE you right code. If you want to do a python venv, its a bit easier to do that before you start writing code and downloading dependencies
 * test test test. Having unit tests makes refactoring later a lot easier (you can make sure you still provide old functionality)

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

Something that will be cool to do is to create my own little website/intranet thing. I host a very simple set of html pages with CSS and JS supported by this browser. You can then navigate through these pages to see how the browser functions. Yay!! 

# Thoughts

Currently, I am about done with chapter 3 and thinking ahead to CSS and JS implementations. What may be a good idea is to extend my current text 'tags' array concept to css classes. I'll also make sure I have a better lexer for my html

# TODOS
* Setup a testing framework (done)
* Moar tests (difficult to do for some classes)
* setup documentation of classes/methods 
* Once done, re-write in C++ with better design patterns. (lol, probably won't)
* Horizontal scrolling
* scrolling for different platforms/OS
* on browser resize, don't reset scroll amount but instead make it proportional to original scroll (done)
* heading tags!!!!! REEEEEEEEEEE (just all the tags in general)
* Currently the browser runs the HTML parser twice on first startup (not the http request because that is cached) likely due to the first tkinter config event. Make sure this doesn't happen when we switch libraries.
* TODO: nice syntax highlighting for view source.
* gitignore should ignore pycache (done)
* env file for debugging (allow for debugging individual modules would be cool: this is what Hadoop/Spark/Hive/HBase do)
* decide if/how to support external fonts (if that is in scope). It may be possible to create custom fonts dynamically??? 
* tool that analyzes code base for code smells and such
* display: none
* Block layout into different classes since I think it is doing a bit much. (done)
* Support basic translation?? that would be cool
* generate documentation for the code (Doxygen is an option but let's use something new) (done)
* [Understand and cleanup imports](https://towardsdatascience.com/how-to-fix-modulenotfounderror-and-importerror-248ce5b69b1c/)
* [Join the discussion](https://github.com/browserengineering/book/discussions)
* center tag and center text
* Preformatted tags (doing)
* Nested CSS selector (done)
* Move Element and Text classes into a different folder.
* Make concrete class for DFAs
* make HTML parser handle errors more gracefully. Maybe rework the DFA there entirely at some point
* stop inheriting background-color once we move away from tkinter
* Implement paragraph spacing with default margin!!

# BUGS

* seems like the bottom text of the page gets cut off in some sites
* HTML parser seems like it is struggling on url https://javascript.info/currying-partials 
* I have assumed you can't have tags inside of li elements. You can, and when this happens I render extra bullet points. The solution is to prepend an extra text element to a li when we encounter it to handle the bullet point. Need to be sure to check that there isn't already a bullet point there though (maybe a specialized class for this).
* for inline elements, the width we draw the rect is just marginally too long (because of trailing space)
* bug in HTML parser when extracting inner attributes. If an attribute starts on a new line we don't get rid of the newline and the attribute will start with a "\n"
* don't just fail if we can't fetch a stylesheet




# WishList

* support some basic svg
* Basic animations (which might end up being doable Interestingly enough)
* gifs 
* Parse selectors [according to their official grammar](https://drafts.csswg.org/selectors/#grammar)

# Resources

A list of docs (not necessarily all the latest) that define HTML/CSS etc specifications. These docs are the official w3 docs, not anything like geeksforgeeks and the like.

* https://html.spec.whatwg.org/multipage/
* https://www.w3.org/TR/2009/CR-CSS2-20090908/visuren.html#visual-model-intro -> old but useful it seems
* https://www.w3.org/TR/css-position-3/#intro -> for positioning if we want to get around to that. 
* https://www.w3.org/TR/2009/CR-CSS2-20090908/box.html
* https://www.w3.org/TR/2009/CR-CSS2-20090908/visudet.html#containing-block-details

Below are projects to take inspiration from (eg: rendering engines).

* https://github.com/Kozea/WeasyPrint
* https://github.com/philborlin/CSSBox

Some other guides 

* https://limpet.net/mbrubeck/2014/08/08/toy-layout-engine-1.html
* https://web.dev/articles/howbrowserswork