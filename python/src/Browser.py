import tkinter
from URL import URL, lex
WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()

    def load(self, url):
        # ...
        #self.canvas.create_rectangle(10, 20, 400, 300)
        #self.canvas.create_oval(100, 100, 150, 150)
        #self.canvas.create_text(200, 150, text="Hi!")
        body = url.request()

        HSTEP, VSTEP = 13, 18
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in lex(body, url.viewSource):
            self.canvas.create_text(cursor_x, cursor_y, text=c)
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP

if __name__ == "__main__":
    import sys
    Browser().load(URL())
    tkinter.mainloop()