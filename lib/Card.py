from tkinter import *
from tkinter import messagebox


class Card:
    def __init__(self, canvas, GRID_SIZE, x, y, title='blank', color = 'white', size=(3, 3), font = '', font_size = 0, sideways=False, tags=()):
        self.canvas = canvas
        self.GRID_SIZE = GRID_SIZE
        self.dragging = False
        self.title = title
        self.color = color
        self.size_x = size[0] * GRID_SIZE
        self.size_y = size[1] * GRID_SIZE

        self.prev_width = 1

        self.tl, self.config_tl = None, None
        if type(tags) == 'str':
            tags = (tags,)
        tags = tags + ('card',)
        self.card = self.canvas.create_rectangle(x, y, x + self.size_x, y + self.size_y, fill=self.color, outline='black', tags=tags)
        self.font_size = font_size
        self.sideways = False if sideways=='False' or not sideways else True
        if font_size == 0:
            self.font_size = max(7, 35 - int(len(self.title)*2.3))
        self.text = self.canvas.create_text(x + int(self.size_x/2), y + int(self.size_y/2), text = self.title, font=("Consolas" if font == '' else font, self.font_size), fill='black', anchor='center', tags=tags, angle=90 if self.sideways else 0)
        #self.t = Label(self.canvas, text='hello', justify='center', wraplength=40)
        #self.t.place(x=x+int(self.size_x/2), y=y+int(self.size_y/2))
        self.canvas.tag_bind(self.card, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.card, "<ButtonRelease-1>", self.stop_drag)
        self.canvas.tag_bind(self.text, "<ButtonRelease-1>", self.stop_drag)
        self.canvas.tag_bind(self.card, "<Button-2>", self.flip)
        self.selected = False
        self.face_up = False
        self.flip(None)

    def get_ids(self):
        return (self.card, self.text)
    def is_selected(self):
        return self.selected
    
    def select(self, event = None):
        self.canvas.lift(self.card)
        self.canvas.lift(self.text)
        self.canvas.itemconfig(self.card, outline='blue', width=1)
        self.selected = True

    def deselect(self, event = None):
        if self.face_up:
            self.canvas.itemconfig(self.card, outline='black')
        else:
            self.canvas.itemconfig(self.card, outline=self.color)
        self.prev_width
        self.canvas.itemconfig(self.card, width=self.prev_width)
        self.selected = False
        
    def delete(self):
        q = messagebox.askquestion(title="Delete", message='Delete \'' + self.title + '\'?')
        if q == 'yes':
            self.canvas.delete(self.card)
            self.canvas.delete(self.text)
        else:
            return False
        return True
    
    def flip(self, event, side_set = -1):
        if side_set != -1:
            self.face_up = side_set
        if (self.face_up):
            self.canvas.itemconfig(self.text, fill='#aaaaaa')
            self.canvas.itemconfig(self.card, dash=2)
        else:
            self.canvas.itemconfig(self.text, fill=self.color)
            self.canvas.itemconfig(self.card, dash=1)
        self.face_up = not self.face_up


    def set_position(self, x, y, xoffset, yoffset):
        c = self.canvas.coords(self.card)
        length = c[2] - c[0]
        height = c[3] - c[1]
        self.canvas.coords(self.card, x+xoffset, y+yoffset, x+xoffset+length, y+yoffset+height)
        self.canvas.coords(self.card, x+xoffset, y+yoffset, x+xoffset+length, y+yoffset+height)
    def move(self, x, y):
        self.canvas.lift(self.card)
        self.canvas.coords(self.card, x, y, x+self.size_x, y+ self.size_y)
        self.canvas.coords(self.text, x + self.size_x - 10, y + 10)
        self.canvas.lift(self.text)
    def drag(self, event):
        if not (str(event).__contains__('Shift') or str(event).__contains__('Control')):
            if not self.dragging:
                c = self.canvas.coords(self.card)
                self.x1 = event.x - c[0]
                self.y1 = event.y - c[1]
                c = self.canvas.coords(self.text)
                self.tx1 = event.x - c[0]
                self.ty1 = event.y - c[1]
                self.dragging = True
                self.select()
            x = event.x
            y = event.y
            self.canvas.lift(self.card)
            self.canvas.coords(self.card, x - self.x1, y - self.y1, x - self.x1 +self.size_x, y - self.y1 + self.size_y)
            self.canvas.coords(self.text, x - self.tx1, y - self.ty1)
            self.canvas.lift(self.text)
    def stop_drag(self, event=None):
        self.dragging = False
        self.x1, self.y1 = 0, 0

        c = self.canvas.coords(self.card)
        #if (c[0] + (c[2]-c[0])/2) % s > s/2:
        if (c[0]) % self.GRID_SIZE < self.GRID_SIZE/2:
            c[0] = c[0] - (c[0] % self.GRID_SIZE)
        else:
            c[0] = c[0] + self.GRID_SIZE - (c[0] % self.GRID_SIZE)

        #if (c[1] + (c[3]-c[1])/2) % s > s/2:
        if (c[1]) % self.GRID_SIZE < self.GRID_SIZE/2:
            c[1] = c[1] - (c[1] % self.GRID_SIZE)
        else:
            c[1] = c[1] + self.GRID_SIZE - (c[1] % self.GRID_SIZE)
        self.deselect()
        self.canvas.itemconfig(self.card, outline='black')
        self.canvas.coords(self.card, c[0], c[1], c[0] + self.size_x, c[1] + self.size_y)
        self.canvas.coords(self.text, c[0] + int(self.size_x/2), c[1] + int(self.size_y/2))
        c = self.canvas.coords(self.card)
        for item in self.canvas.find_enclosed(c[0]+1, c[1]+1, c[2]-1, c[3]-1):
            if item is not self.text:
                self.canvas.tag_raise(item)


def test():
    root = Tk()
    root.geometry('1000x800')
    canvas = Canvas(root)
    canvas.pack(fill=BOTH, expand=1)
    card = Card(canvas, 25, 0, 0,  title='hello', color='red', font='times', font_size=20, sideways=True, size=(6, 10))
    root.mainloop()

if __name__ == '__main__':
    test()