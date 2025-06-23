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