import tkinter as tk
from tkinter import *
from lib.InfiniteCanvas import InfiniteCanvas
import lib.SimpleDialog as dialouge
import re
import os
from tkinter import messagebox

GRID_SIZE = 30
MAX_ZOOM = 1.8
MIN_ZOOM = 0.3

cards= []

def normalize(value, _max = MAX_ZOOM, _min = MIN_ZOOM):
    return round((value - _min) / (_max - _min), 4)
def get_selected():
    result = []
    for card in cards:
        if card.is_selected():
            result.append(card)
    return result
def toRGBA(color):
    return tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
def toHex(color):
    return ('#%02x%02x%02x%02x' % color)[:7]
def brighten(color, percent):
    if percent > 1:
        percent /= 100
    rgba = toRGBA(color)
    result = []
    white = False
    if rgba[0] + rgba[1] + rgba[2] > 600:
        white = True
    for i in range(3):
        if not white:
            result.append(min(int(rgba[i]*(1 + percent)), 255))
        else:
            result.append(min(int(rgba[i]* (percent*3)), 255))
    return toHex((result[0], result[1], result[2], 255))

class InfiniteCanvasCard(InfiniteCanvas):
    '''
    Initial idea by Nordine Lofti
    https://stackoverflow.com/users/12349101/nordine-lotfi
    written by Thingamabobs
    https://stackoverflow.com/users/13629335/thingamabobs

    The infinite canvas allows you to have infinite space to draw.
    
    You can move around the world as follows:
    - MouseWheel for Y movement.
    - Shift-MouseWheel will perform X movement.
    - Alt-Button-1-Motion will perform X and Y movement.
    (pressing ctrl while moving will invoke a multiplier)

    Additional features to the standard tk.Canvas:
    - Keeps track of the viewable area
    --> Acess via InfiniteCanvas().viewing_box()
    - Keeps track of the visibile items
    --> Acess via InfiniteCanvas().inview()
    - Keeps track of the NOT visibile items
    --> Acess via InfiniteCanvas().outofview()

    Also a new standard tag is introduced to the Canvas.
    All visible items will have the tag "inview"
    '''

    def __init__(self, master, bg_color = '#1b1b1b', grid_color = '#2b2b2b', **kwargs, ):
        super().__init__(master, **kwargs)

        self._x_pos         = 0     #viewed position in x direction
        self._y_pos         = 0     #viewed position in y direction
        self._xshifted      = 0     #view moved in x direction
        self._yshifted      = 0     #view moved in y direction
        self._zoom_val      = 1.0   #level of zoom

        self.a = False
        self.ORIGIN         = self.create_oval(-1, -1, 1, 1, fill='', outline='')
        self.center         = self.create_oval(398, 248, 401, 251, fill='white', outline='black')
        self.coord_text     = self.create_text(3, 10, fill='', font=('Consolas', 11), justify='left', anchor='w', tags='coords')
        self.selection_box  = self.create_rectangle(0, 0, 0, 0, fill='', outline='blue', tags='selection')
        #'#890b0b'

        self.bg_color = bg_color
        self.grid_color = grid_color
        self.grid_lines = []
        self.indicators = []
        self.dragging = False
        self.config_tl = None
        self.x1, self.y1 = 0, 0
        self.configure(confine=False, highlightthickness=0, bd=0, background=self.bg_color)
        self.bind('<MouseWheel>',    self._scroll)
        #self.bind("<MouseWheel>", self._zoom)
        root.update()
        root.bind("<space>", self._set_position)
        root.bind("<FocusIn>", self._remove_config)
        #root.bind('a', self.selecting_on)
        root.bind('<KeyRelease>', self.selecting_off)
        #root.bind('f', self._search)
        root.bind('<Configure>', self._update_center)
        self.bind('<B1-Motion>', self._select)
        self.bind('<Button-1>', self._deselect_all)
        self.bind('<ButtonRelease-1>', self._select_un)

        self._set_position(None, 400, 250)
        self._create_grid()
        return None

    def selecting_on(self, event=None):
        self.a = True

    def selecting_off(self, event=None):
        self.a = False

    def viewing_box_center(self) -> tuple:
        'Returns a tuple of the form x1,y1 represents center of area'
        x1 = self._xshifted
        y1 = self._yshifted
        x2 = self.winfo_width()+self._xshifted
        y2 = self.winfo_height()+self._yshifted
        return (x1+int((x2 - x1)/2), y1+int((y2- y1)/2))
    
    def viewing_box(self) -> tuple:
        'Returns a tuple of the form x1,y1,x2,y2 represents visible area'
        x1 = self._xshifted
        y1 = self._yshifted
        x2 = self.winfo_width()+self._xshifted
        y2 = self.winfo_height()+self._yshifted
        return x1,y1,x2,y2

    def inview(self) -> set:
        'Returns a set of identifiers that are currently viewed'
        return set(self.find_overlapping(*self.viewing_box()))

    def outofview(self) -> set:
        'Returns a set of identifiers that are currently not viewed'
        all_ = set(self.find_withtag('card'))
        return all_ - self.inview()
    
    def _zoom(self, event):
        #Zoom feature does not work
        xorigin, yorigin = self.viewing_box_center()
        b = self.create_rectangle(xorigin-2, yorigin-2, xorigin+2, yorigin+2)
        if event.delta < 0 and self._zoom_val <= MAX_ZOOM:
            self._zoom_val += 0.02
            canvas.scale('all', xorigin, yorigin, 0.9799, 0.9799)
        elif event.delta > 0 and self._zoom_val >= MIN_ZOOM:
            self._zoom_val -= 0.02
            canvas.scale('all', xorigin, yorigin, 1.0205, 1.0205)
        
        self._update_coords()

    def _create_grid(self):
        for i in range(0 - 500*GRID_SIZE, 500*GRID_SIZE, GRID_SIZE):
            if i != 0:
                l = self.create_line(-10000, i, 10000, i, fill=self.grid_color, width=1)
                self.lower(l)
                self.grid_lines.append(l)
                l = self.create_line(i, -10000, i, 10000, fill=self.grid_color, width=1)
                self.lower(l)
                self.grid_lines.append(l)
        
        l = self.create_line(-10000, 0, 10000, 0, fill=brighten(self.grid_color, 0), width=0)
        self.grid_lines.append(l)
        l = self.create_line(0, -10000, 0, 10000, fill=brighten(self.grid_color, 0), width=0)
        self.grid_lines.append(l)

    def _config(self):
        self.config_tl = Toplevel(root)
        self.config_tl.resizable(False, False)
        x = (self.config_tl.winfo_screenwidth() - self.config_tl.winfo_reqwidth()) // 2
        y = (self.config_tl.winfo_screenheight() - int(self.config_tl.winfo_reqheight()/2)) // 2
        self.config_tl.geometry('200x60+%d+%d' % (x, y))
        self.config_tl.title('Settings')


        def bg_color(event):
            color = sv.get()
            if color[0] != '#':
                e.select_range(0, 10000)
                return
            try:
                self.config(background=color)
                self.bg_color = color
            except:
                e.select_range(0, 10000)
        sv = StringVar(None, str(self.bg_color))
        Label(self.config_tl, text='Color:').grid(row=0, column=0, padx=10)
        e = Entry(self.config_tl, textvariable=sv, width=10, relief='flat')
        e.grid(row=0, column=1, columnspan=2)
        e.bind("<Return>", bg_color)


        def grid_color(event):
            color = sv2.get()
            if color[0] != '#':
                e2.select_range(0, 10000)
                return
            try:
                for line in self.grid_lines:
                    self.itemconfig(line, fill=color)
                    if 0 in self.coords(line):
                        self.itemconfig(line, fill=brighten(color, 25))
                self.grid_color = color
            except:
                e2.select_range(0, 10000)
        sv2 = StringVar(None, str(self.grid_color))
        Label(self.config_tl, text='Grid Color:').grid(row=1, column=0, padx=10)
        e2 = Entry(self.config_tl, textvariable=sv2, width=10, relief='flat')
        e2.grid(row=1, column=1, columnspan=2)
        e2.bind("<Return>", grid_color)

        self.config_tl.mainloop()

    def _remove_config(self, event=None):
        self._select()
        print(self.config_tl)
        if self.config_tl != None:
            self.config_tl.destroy()
            self.config_tl = None

    def _set_position(self, event=None, x = 0, y = 0):
        if x == 0 and y == 0:
            x = int(root.winfo_width()/2)
            y = int(root.winfo_height()/2)
        self._xshifted=0
        self._yshifted=0
        self._x_pos = int(root.winfo_width()/2) * self._zoom_val
        self._y_pos = int(root.winfo_height()/2)
        self.xview(MOVETO, 1)
        self.yview(MOVETO, 1)
        if(self.center != 2):
            self._update_center()
        self._update_coords()

        if self._zoom_val < 1.0:
            self.scale('all', 400, 250, self._zoom_val, self._zoom_val)
        elif self._zoom_val > 1.0:
            self.scale('all', 400, 250, self._zoom_val + (0.45 * (normalize(self._zoom_val))), self._zoom_val + (0.45 * (normalize(self._zoom_val)-0.5)))
        c = self.coords(self.ORIGIN)
        self._zoom_val = 1.0

    def _update_tags(self):
        vbox = self.viewing_box()
        self.addtag_overlapping('inview',*vbox)
        inbox = set(self.find_overlapping(*vbox))
        witag = set(self.find_withtag('inview'))
        [self.dtag(i, 'inview') for i in witag-inbox]
        self.viewing_box()
        
    def _create(self, *args):
        ident = super()._create(*args)
        self._update_tags()
        return ident
    
    def _select_object(self):
        c = self.viewing_box()
        for item in self.find_overlapping(c[0], c[1], c[2], c[3]):
            if 'card' in self.gettags(item):
                find_card(item).deselect()
            
        c = self.viewing_box_center()
        for item in self.find_overlapping(c[0], c[1], c[0], c[1]):
            if 'card' in self.gettags(item):
                find_card(item).select()

    def _update_center(self, event=None):
        c = self.viewing_box_center()
        self.coords(self.center, c[0]-2, c[1]-2, c[0]+1, c[1]+1)
        self._select_object()
        self._update_indicators
        self.tag_raise(self.center)

    
    def _update_coords(self):
        c = self.viewing_box_center()
        bbox_c = self.bbox(self.ORIGIN, self.center)
        x,  y = 0, 0
        if c[0] < -1:
            x = -round( (bbox_c[2] - bbox_c[0] / GRID_SIZE) - 1, 2)
        elif c[1] > 1:
            x = round( -(bbox_c[0] - bbox_c[2] / GRID_SIZE) - 1, 2)
        if c[1] < -1:
            y = round( (bbox_c[3] - bbox_c[1] / GRID_SIZE) - 1, 2)
        elif c[1] > 1:
            y = -round( -(bbox_c[1] - bbox_c[3] / GRID_SIZE) - 1, 2)
        self.canvas_coordinates = 'X ' + str(x) + ' Y ' + str(y)
        c = self.viewing_box()
        self.coords(self.coord_text, c[0]+3, c[1]+10)
        self.itemconfig(self.coord_text, text=self.canvas_coordinates)
        self.tag_raise('coords')

    def _update_indicators(self):
        for indicator in self.indicators:
            self.delete(indicator)
        for num in self.outofview():
            c = self.coords(num)
            view_c = self.viewing_box()
            if len(c) == 4:
                card = find_card(num)
                card_coords = self.coords(card.card)
                ''' line system to card'''
                #card_coords = (int(card_coords[0] + ((card_coords[2] - card_coords[0])/2)), int(card_coords[1] + ((card_coords[3] - card_coords[1])/2)))
                #view_coords = (int(view_c[0] + ((view_c[2] - view_c[0])/2)), int(view_c[1] + ((view_c[3] - view_c[1])/2)))
                #dist = int(((card_coords[0] - view_coords[0]) **2 + (card_coords[1] - view_coords[1]) **2) / 10000)
                #dist = int(((card_coords[0] - 0) **2 + (card_coords[1] - 0) **2) / 10000)
                #i = self.create_line(card_coords[0], card_coords[1], view_coords[0], view_coords[1], fill='pink', dash=(1, min(127, dist)))
                #i = self.create_line(card_coords[0], card_coords[1], 0, 0, fill='pink', dash=(1, min(127, dist)))
                #self.indicators.append(i)
                coords = view_c[0] + 5, view_c[1] + 5, view_c[2] - 5, view_c[3] - 5
                #i = self.create_rectangle(coords, fill='', outline=card.color, dash=(50, 125), dashoffset=100)
                #self.indicators.append(i)
        
        ''' line system to origin'''

        view_c = self.viewing_box()
        x1, y1 = int(view_c[0] + ((view_c[2] - view_c[0])/2)), int(view_c[1] + ((view_c[3] - view_c[1])/2))
        x2, y2 = max(min((0 - x1)/100, 10), -10), max(min((0 - y1) / 100, 10), -10)
        #i = self.create_line(x1, y1, 0, 0, fill='pink')
        #self.indicators.append(i)
        #i = self.create_line(x1, y1, x1 + x2, y1 + y2, fill='cyan', dash=(1, 2), width = 10)
        #self.indicators.append(i)
        i = self.create_line(x1, y1, x1 + x2, y1 + y2, fill='#8b8b8b', dash=(1, 2))
        self.indicators.append(i)

    def _wheel_scroll(self, xy, amount):
        cx,cy = self.winfo_rootx(), self.winfo_rooty()
        self.scan_mark(cx, cy)
        if xy == 'x': x,y = cx+amount, cy
        elif xy == 'y': x,y = cx, cy+amount
        name = f'_{xy}shifted'
        setattr(self,name, getattr(self,name)-(amount*2))
        c = self.viewing_box_center()
        self._x_pos = c[0] * self._zoom_val
        self._y_pos = c[1] * self._zoom_val
        self.scan_dragto(x,y, gain=2)
        self._update_tags()
        self._select_object()
        self._update_center()
        self._update_coords()
        self._update_indicators()

        c = self.viewing_box_center()
        if (self.a):
            cards = get_selected()
            for i in cards:
                i.set_position(c[0], c[1], 0, 0)

    def _scroll(self,event):
        self._wheel_scroll('x' if event.state else 'y', int(event.delta*4.75*self._zoom_val))

    def _select_un(self, event=None):
        if 'selection' in self.gettags(self.selection_box):
            for item in self.find_enclosed(*self.coords(self.selection_box)):
                if 'card' in self.gettags(item):
                    find_card(item).select()
            canvas.delete(self.selection_box)
            self.selection_box = self.create_rectangle(0, 0, 0, 0, fill='', outline='blue', tags='selection')
            self.x1, self.y1 = 0, 0
        self.dragging = False

    def _deselect_all(self, event=None):
        for i in get_selected():
            i.deselect()

    def _select(self, event=None):
        canvas.delete(self.selection_box)
        c = self.viewing_box()
        go = True
        if not self.dragging:
            for i in self.find_overlapping(c[0]+event.x, c[1]+event.y, c[0]+event.x, c[1]+event.y):
                if 'card' in self.gettags(i):
                    go = False
            if go:
                self.x1 = c[0] + event.x
                self.y1 = c[1] + event.y
                self.dragging = True
        x, y = 0, 0
        if go:
            x = c[0] + event.x
            y = c[1] + event.y
        self.selection_box = self.create_rectangle(self.x1, self.y1, x, y, fill='', outline='blue', tags='selection')
    def _search(self, event=None):
        root.bind('<Return>')
        def look(event=None):
            user_input = sv.get()
            for card in cards:
                if str(card.title).lower().__contains__(str(user_input).lower()):
                    b = self.bbox(card.card, self.ORIGIN)
                    x, y = b[2]-b[0], b[3]-b[1]
                    for item in self.find_all():
                        c = self.coords(item)
                        if len(c) == 2:
                            self.coords(item, c[0] + x, c[1] + y)
                        else:
                            self.coords(item, c[0]+x, c[1]+y, c[2]+x, c[3]+y)

            e.destroy()
            #root.bind("<Return>", activate_selected)
        sv = StringVar(None)
        e = Entry(canvas, width=20, relief='flat', textvariable=sv)
        e.place(x=int(root.winfo_width()/2-100),y=100)
        e.bind("<Return>", look)




class Card:
    def __init__(self, x, y, title='blank', color = 'white', size=(3, 3), font = '', font_size = 0, sideways=False):
        self.dragging = False
        self.title = title
        self.color = color
        self.size_x = size[0] * GRID_SIZE
        self.size_y = size[1] * GRID_SIZE

        try:
            self.file = open("./cards/" + str(self.title) + ".txt" , "r")
        except:
            self.file = open("./cards/" + str(self.title) + ".txt" , "w")
        self.tl, self.config_tl = None, None
        self.card = canvas.create_rectangle(x, y, x + self.size_x, y + self.size_y, dash=2, fill=self.color, outline='black', tags='card')
        self.font_size = font_size
        self.sideways = True if sideways=='True' else False
        if font_size == 0:
            self.font_size = max(7, 35 - int(len(self.title)*2.3))
        self.text = canvas.create_text(x + int(self.size_x/2), y + int(self.size_y/2), text = self.title, font=("Consolas" if font == '' else font, self.font_size), fill='black', anchor='center', tags='card', angle=90 if self.sideways else 0)
        #self.t = Label(canvas, text='hello', justify='center', wraplength=40)
        #self.t.place(x=x+int(self.size_x/2), y=y+int(self.size_y/2))
        canvas.tag_bind(self.card, "<B1-Motion>", self.drag)
        canvas.tag_bind(self.text, "<B1-Motion>", self.drag)
        canvas.tag_bind(self.card, "<ButtonRelease-1>", self.stop_drag)
        canvas.tag_bind(self.text, "<ButtonRelease-1>", self.stop_drag)
        canvas.tag_bind(self.card, "<Button-2>", self.flip)
        self.selected = False
        self.face_up = False
        self.flip(None)

        def destroy(event):
            if canvas.config_tl:
                canvas.config_tl.destroy()
                canvas.config_tl = None
            if self.config_tl:
                self.config_tl.destroy()
                self.config_tl = None
            if self.tl:
                self.tl.destroy()
                self.tl = None
        root.bind("<FocusIn>", destroy)
    def get_ids(self):
        return (self.card, self.text)
    def is_selected(self):
        return self.selected
    def open(self, event = None):
        import subprocess
        subprocess.call(['open', '-a', 'TextEdit', "./cards/" + str(self.title) + '.txt'])
        '''if not self.tl:
            self.tl = Toplevel(root)
            x = (self.tl.winfo_screenwidth()) / 2 - 300
            y = (self.tl.winfo_screenheight()) / 2 - 225
            self.tl.wm_geometry('600x450+%d+%d' % (x, y))
            self.tl.lift()
            self.tl.title(self.title)
            def on_closing():
                self.tl.destroy()
                self.tl = None

            self.tl.protocol("WM_DELETE_WINDOW", on_closing)
            self.tl.mainloop()
        else:
            self.tl.lift()'''

    def config(self, event = None):
        #['Size', 'Color', 'Font', 'Title']
        self.config_tl = Toplevel(root)
        self.config_tl.resizable(False, False)
        self.config_tl.title('Configure ' + self.title)
        x = (self.config_tl.winfo_screenwidth()) / 2 - 100
        y = (self.config_tl.winfo_screenheight()) / 2 - 75
        self.config_tl.wm_geometry('220x150+%d+%d' % (x, y))

        x = (self.config_tl.winfo_screenwidth() - self.config_tl.winfo_reqwidth()) // 2
        y = (self.config_tl.winfo_screenheight() - int(self.config_tl.winfo_reqheight()/2)) // 2
        self.config_tl.wm_geometry('+%d+%d' % (x, y))
        buttons = ['Size', 'Color', 'Font', 'Title']
        #self.frame = Frame(self.config_tl)
        #self.frame.pack()


        def resize(event):
            try:
                x, y = sv.get().split()
                self.size_x = int(x) * GRID_SIZE
                self.size_y = int(y) * GRID_SIZE
                c = canvas.coords(self.card)
                canvas.coords(self.card, c[0], c[1], c[0] + self.size_x, c[1] + self.size_y)
                canvas.coords(self.text, c[0] + int(self.size_x/2), c[1] + int(self.size_y/2))
            except:
                e.select_range(0, 10000)
        sv = StringVar(None, str(int(self.size_x/GRID_SIZE)) + ' ' + str(int(self.size_y/GRID_SIZE)))
        Label(self.config_tl, text='Size:').grid(row=0, column=0, padx=10, sticky='e')
        e = Entry(self.config_tl, textvariable=sv, width=10, relief='flat')
        e.grid(row=0, column=1, columnspan=2)
        e.bind("<Return>", resize)

        def recolor(event):
            color = sv2.get()
            try:
                canvas.itemconfig(self.card, fill=color)
                self.color = color
                if self.color == 'black':
                    canvas.itemconfig(self.text, fill='white')
                else:
                    canvas.itemconfig(self.text, fill='black')
            except:
                canvas.itemconfig(self.card, fill=self.color)
                e2.select_range(0, 10000)
        sv2 = StringVar(None, str(self.color))
        Label(self.config_tl, text='Fill:', justify='left', anchor='e').grid(row=1, column=0, padx=10, sticky='e')
        e2 = Entry(self.config_tl, textvariable=sv2, width=10, relief='flat')
        e2.grid(row=1, column=1, columnspan=2)
        e2.bind("<Return>", recolor)

        def recolor_text(event):
            color = sv3.get()
            try:
                canvas.itemconfig(self.text, fill=color)
            except:
                e2.select_range(0, 10000)

        sv3 = StringVar(None, str(canvas.itemcget(self.text, 'fill')))
        Label(self.config_tl, text='Text Color:', justify='right', anchor='e').grid(row=2, column=0, padx=10, sticky='e')
        e3 = Entry(self.config_tl, textvariable=sv3, width=6, relief='flat')
        e3.grid(row=2, column=1, columnspan=1)
        e3.bind("<Return>", recolor_text)

        def flip_text(event=None):
            try:
                if int(canvas.itemcget(self.text, 'angle').split('.')[0]) != 90:
                    canvas.itemconfig(self.text, angle=90)
                    self.sideways = True
                else:
                    e31.deselect()
                    canvas.itemconfig(self.text, angle=0)
                    self.sideways = False
            except:
                pass
        e31 = Radiobutton(self.config_tl, width=1, command=flip_text, relief='flat')
        e31.grid(row=2, column=2, columnspan=2)


        def font(event):
            font = sv4.get()
            size = sv5.get()
            try:
                canvas.itemconfig(self.text, font=(font, int(size)))
                self.font_size = size
            except:
                e4.select_range(0, 10000)
                e5.select_range(0, 10000)
        sv4 = StringVar(None, str(canvas.itemcget(self.text, 'font').split()[0]))
        sv5 = StringVar(None, str(re.search(r'\d+', canvas.itemcget(self.text, 'font')).group()))
        Label(self.config_tl, text='Font:', justify='right', anchor='e').grid(row=3, column=0, padx=10, sticky='e')
        e4 = Entry(self.config_tl, textvariable=sv4, width=5, relief='flat')
        e4.grid(row=3, column=1)
        e5 = Entry(self.config_tl, textvariable=sv5, width=3, relief='flat')
        e5.grid(row=3, column=2)
        e4.bind("<Return>", font)
        e5.bind("<Return>", font)


        def retitle(event):
            title = sv6.get()
            try:
                font_size = 35 - int(len(self.title)*2.3)
                font = canvas.itemcget(self.text, 'font').split()[0]
                sv5.set(str(font_size))
                canvas.itemconfig(self.text, text=title, font=(font, font_size))
                self.config_tl.title("Configure " + title)

                old = open('./cards/'+ self.title +'.txt', 'r')
                new = open('./cards/' + title + '.txt', 'a')
                for line in old:
                    new.write(line)
                os.remove("./cards/" + self.title + ".txt")
                self.title = title
            except:
                e6.select_range(0, 10000)
        sv6 = StringVar(None, str(self.title))
        Label(self.config_tl, text='Title:', justify='right', anchor='e').grid(row=4, column=0, padx=10, sticky='e')
        e6 = Entry(self.config_tl, textvariable=sv6, width=10, relief='flat')
        e6.grid(row=4, column=1, columnspan=2)
        e6.bind("<Return>", retitle)

        self.config_tl.mainloop()

    def select(self, event = None):
        canvas.lift(self.card)
        canvas.lift(self.text)
        canvas.itemconfig(self.card, outline='blue')
        canvas.itemconfig(self.card, width=2)
        self.selected = True
    def deselect(self, event = None):
        canvas.itemconfig(self.card, outline='black')
        canvas.itemconfig(self.card, width=1)
        if self.tl != None:
            self.tl.destroy()
        if self.config_tl != None:
            self.config_tl.destroy()
        self.selected = False
    def set_position(self, x, y, xoffset, yoffset):
        c = canvas.coords(self.card)
        length = c[2] - c[0]
        height = c[3] - c[1]
        canvas.coords(self.card, x+xoffset, y+yoffset, x+xoffset+length, y+yoffset+height)
        canvas.coords(self.card, x+xoffset, y+yoffset, x+xoffset+length, y+yoffset+height)
    def move(self, x, y):
        canvas.lift(self.card)
        canvas.coords(self.card, x, y, x+self.size_x, y+ self.size_y)
        canvas.coords(self.text, x + self.size_x - 10, y + 10)
        canvas.lift(self.text)
    def drag(self, event):
        if not (str(event).__contains__('Shift') or str(event).__contains__('Control')):
            if not self.dragging:
                c = canvas.coords(self.card)
                self.x1 = event.x - c[0]
                self.y1 = event.y - c[1]
                c = canvas.coords(self.text)
                self.tx1 = event.x - c[0]
                self.ty1 = event.y - c[1]
                self.dragging = True
                self.select()
            x = event.x
            y = event.y
            canvas.lift(self.card)
            canvas.coords(self.card, x - self.x1, y - self.y1, x - self.x1 +self.size_x, y - self.y1 + self.size_y)
            canvas.coords(self.text, x - self.tx1, y - self.ty1)
            canvas.lift(self.text)
    def stop_drag(self, event=None):
        self.dragging = False
        self.x1, self.y1 = 0, 0

        c = canvas.coords(self.card)
        #if (c[0] + (c[2]-c[0])/2) % s > s/2:
        if (c[0]) % GRID_SIZE < GRID_SIZE/2:
            c[0] = c[0] - (c[0] % GRID_SIZE)
        else:
            c[0] = c[0] + GRID_SIZE - (c[0] % GRID_SIZE)

        #if (c[1] + (c[3]-c[1])/2) % s > s/2:
        if (c[1]) % GRID_SIZE < GRID_SIZE/2:
            c[1] = c[1] - (c[1] % GRID_SIZE)
        else:
            c[1] = c[1] + GRID_SIZE - (c[1] % GRID_SIZE)
        self.deselect()
        canvas.itemconfig(self.card, outline='black')
        canvas.coords(self.card, c[0], c[1], c[0] + self.size_x, c[1] + self.size_y)
        canvas.coords(self.text, c[0] + int(self.size_x/2), c[1] + int(self.size_y/2))
        c = canvas.coords(self.card)
        for item in canvas.find_enclosed(c[0]+1, c[1]+1, c[2]-1, c[3]-1):
            if item is not self.text:
                canvas.tag_raise(item)
    def flip(self, event, side_set = -1):
        if side_set != -1:
            self.face_up = side_set
        if (self.face_up):
            canvas.itemconfig(self.text, fill= self.color)
            canvas.itemconfig(self.card, dash=2)
        else:
            canvas.itemconfig(self.text, fill='black')
            canvas.itemconfig(self.card, dash=1)
        self.face_up = not self.face_up
    def delete(self):
        extra = ''
        if os.path.getsize('./cards/' + self.title + '.txt') > 0:
            extra = '\n Card contains text that will be permanently deleted!'
        q = messagebox.askquestion(title="Delete", message='Delete \'' + self.title + '\'?' + extra)
        if q == 'yes':
            canvas.delete(self.card)
            canvas.delete(self.text)
            try:
                os.remove("./cards/" + self.title + ".txt")
            except:
                pass
        else:
            return False
        return True
    def _get_coords(self):
        return canvas.coords(self)
    def __str__(self):
        c = canvas.coords(self.card)
        return str(self.title.replace(' ', '`')) +' '+ str(int(c[0]/GRID_SIZE)) +' '+ str(int(c[1]/GRID_SIZE)) +' '+ str(int(self.size_x/GRID_SIZE)) +' '+ str(int(self.size_y/GRID_SIZE)) +' '+ str(self.color)+' '+ str(canvas.itemcget(self.text, 'font').split()[0]) +' '+ str(self.font_size) +' '+ str(self.sideways)

def find_card(id) -> Card:
    try:
        for card in cards:
            if id in card.get_ids():
                return card
    except:
        return None

if __name__ == '__main__':

    f = open('__cards.txt', 'r')
    root = tk.Tk()
    root.title('Application')
    root.geometry('800x500')

    canvas_settings = f.readline().split()
    canvas = InfiniteCanvasCard(root, bg_color=canvas_settings[0], grid_color = canvas_settings[1])
    canvas.pack(fill=tk.BOTH, expand=True)

    def save_cards():
        f = open('__cards.txt', 'w')
        f.write((canvas.bg_color) + ' ' + (canvas.grid_color) + '\n')
        for card in cards:
            f.write(str(card) + '\n')
        root.destroy()
    def load_cards(f):
        #try:
        for i in f.readlines()[0:]:
            a = i.split()
            card = Card(int(a[1])*GRID_SIZE, int(a[2])*GRID_SIZE, title=a[0].replace('`', ' '), size=(int(a[3]), int(a[4])), color=a[5], font= a[6], font_size = a[7], sideways = a[8])
            card.stop_drag()
            cards.append(card)
        #except:
        #    f = open('__cards.txt', 'x')

    def new_card():
        title = dialouge.askstring('Create new card', 'Title:')
        if title != '':
            c = canvas.viewing_box()
            card = Card((c[0]) + int((c[2] - c[0])/2), c[1] + int((c[3] - c[1])/2), title)
            card.stop_drag()
            cards.append(card)
    
    def activate_selected(event):
        selected = get_selected()
        if selected == []:
            if event.keysym == 'Return':
                new_card()
            elif event.keysym == 'Control_L':
                canvas._config()
        else:
            for card in selected:
                if event.keysym == 'Return':
                    card.open()
                elif event.keysym == 'Control_L':
                    card.config()
                elif event.keysym == 'BackSpace':
                    if card.delete():
                        cards.remove(card)
                    root.after(1, lambda: root.focus_force())
    
    load_cards(f)
    root.bind("<Return>", activate_selected)
    root.bind("<Control-KeyPress>", activate_selected)
    root.bind("<Key>", activate_selected)
    root.protocol("WM_DELETE_WINDOW", save_cards)
    root.mainloop()