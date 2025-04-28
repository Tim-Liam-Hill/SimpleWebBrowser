
# Chapter 7

So, funnily enough, I ended up implementing the Line and Text layouts myself and this chapter handles that. Interesting!! That's a bit of less work for me. There isn't any first-word pseudo-class so yeah, I don't think I want to use their approach. 

For the click handling, I think I might adjust the approach the book is using. Instead of the list comprehension the book is using, I think I will implement a method on the Layout objects to search for coordinates (since some lower elements don't actually know their x and y coordinates). This will also help us be faster since if our y is out of range we can just return. Nice. 

So the click link navigation works fairly well. Only real issue is alot of the sites I would link to aren't very easy for my browser to handle (due to malformed html and some css exceptions that are on the backburner). Still, progress!