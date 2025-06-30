# Chapter 8

Meow Meow Meow Meow 

Its a good thing we did our rework a little while back, but it does mean we have to integrate the new code into our layout engine. In fact, I think I will have to read through the chapter first to get an idea of what will be implemented since my approach will have to be different from the books. For one, I want to use a different approach for buttons (essentially doing ex 8.8 early).

So input can literally just be a combination of inline layouts? we could have the input layout having the inline layout followed by the input. So InputLayout can hold an inline layout (which is the non-input portion) and directly keep track of the input on the rhs. BUT: are we going to implement labels?? 

One thing to take note of is that there are various types of inputs: text, image, radio buttons etc. May need to subclass for each of them.

So for labels: they will be interpreted as inline layouts and if they are next to the inputs they match to (which I imagine they would normally be) there isn't really a need to handle them differently. In this case, InputLayout can be a standalone class with nothing else special. 

Buttons might be interesting to handle. We could sublass them but I don't think we need to.

Something interesting is that the book uses a button for form submission, but per my understanding it should be ```input type="submit"```. I will implement things that way since in my mind, buttons should always have explicit 'on click' handlers that define what they do. 

So, let's subclass input layout and make:
* text (default)
* submit (different in that it has its own inner text set and a custom on click function). Inner text depends on [value](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/submit) or has a default

They will all be inline in nature, so maybe they should sublass the inline layout ... hmm....

Oh wait: [buttons are used in forms when type is submit](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Your_first_form#the_button_element). Eugh, gonna need some interesting code to handle this. 

I think Ill keep buttons simple and basically reuse the block layout for them. Anything can act as a button so long as it has an 'onclick' method of sorts. Also on click we can check tag to determine if button, or maybe just make button an input type. 

When I get to 8.8 I'll think about button subclass.

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button#notes
https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input

Yeah, my layout engine definitely needs some work ... Hopefully it won't come back  to bite me too much when I get to implementing JS.
I no longer want to use my inheritance pattern for my layout engine, it is making things more complicated for me than they need to be. InputLayout can do its own thing. Maybe I'll come back and make Layout a very very simple class, but until then I am not going to be using it whenever possible. 

Yeah, its time to rework layouts again :/. The reason being is the inline layout class. Specifically:

* Before we only had to worry about 2 kinds of layouts: inline and block
* As such, the lines member of a layout would either only contain lines or only contain one block element
* but now, InputLayout doesn't fit this paradigm
* InputLayout should not go on a new line 
* and it needs to know the x and y coordinates to start at when laying itself out

We may be able to get away with just reworking Inline Layout (as opposed to everything). I think one of the goals should be to have a generic "createLayout" function that can take in a display type and init the layout object in question?

Let's take a better look at how the textbook handled the layout logic in chapter 7 and see if we can get some inspiration. 

# LAYOUT REWORK 
I did attempt a layout rework here but I have decided to scrap that (althought the notes are stilled stored on branch 'failed_relayout'). I am going to go back to the book's layout method so that later chapters can go a lot smoother. 

Maybe eventually I will pull an Andreas Kling and write a better browser for an OS I make myself (~evil laughter~).

So: let's get rid of the fluff in our current layout approach, then make it look a bit more like chapter 7, then add input layout (and then maybe the inline button thing that the exercise wants).

Now that I am removing a bunch of things, i am actually starting to think some of my initial ideas weren't all that bad. Specifically my idea regarding the 'getStartX' and 'getStartY' for Layouts. This would allow us to implement list items rather nice, but yeah. Complicated I guess. Still, KISS then add what we need.

So let's go a little slower now. Very small rework just to clean things up.

* Document Layout child (done)
* Layout getElements at rename (done)
* Layout layout type function -> move to LayoutConstants and rework (done)
* Delete LayoutTypes enum and the Layout layoutType function (done)
* get rid of 'calculateContentWidth' and 'calculateWidth' (done)
* move InlineLayout 'getFont' and rework (done)

So there is some good news and some bad news. The good:
* code is a lot cleaner
* it actually isn't as bad as I initially thought

The bad
* part of our layout algorithm is broken (specifically having block elements on the same line as inline elements)

The good again
* we may as well rework our Inline layout and line layout to be closer to the books, since that should help fix problems down the line.

Okay, so here is the idea:
* An Inline Layout is a collection of Lines
* A line holds a number of Layout-descendant objects
* It also holds a number of rect objects for background displaying (in a separate list)
* every Layout descendant object 
* If a Line holds a Block Layout object, then that is the only element in that line
* Text Fragments will become a new layout object (consider them anon Inline type bois)
* When we flush a line, we just use the getHeight() method to calculate height and then we can work out baseline etc from there. (half leading back up? and maybe keep track of the max descent?)

Who would have thought an elegant solution was within my grasp? Sure as hell not me, and I am still not entirely convinced but I have a good feeling.

