Making this its own notes page since wow, I have been writing a lot of notes 

https://www.w3.org/TR/CSS22/visuren.html

"Certain values of the 'display' property cause an element of the source document to generate a principal box that contains descendant boxes and generated content and is also the box involved in any positioning scheme. Some elements may generate additional boxes in addition to the principal box: 'list-item' elements. These additional boxes are placed with respect to the principal box."

https://www.w3.org/TR/CSS22/visuren.html#display-prop -> will these be our classes?? 

"Boxes in the normal flow belong to a formatting context, which in CSS 2.2 may be table, block or inline. In future levels of CSS, other types of formatting context will be introduced. Block-level boxes participate in a block formatting context. Inline-level boxes participate in an inline formatting context. Table formatting contexts are described in the chapter on tables."

Mayhaps we implement normal flow then??? 

I have been thinking about the original document tree too much: our box layout doesn't have to conform to that. It is separate to the DOM??? Is it? I suppose???!??!?!?! 

It is, the DOM we created was the nodes with Element and Text classes. What we are creating now is different. 

What is the DOM anyway? https://dom.spec.whatwg.org/

Let's take a look at the LadyBird browser mayhaps, or maybe chromium. Git cloning just because I want to look at the source code for inspiration/understanding. 
