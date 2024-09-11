import tkinter as tk

class InfiniteCanvas(tk.Canvas):
    '''
    Initial idea by Nordine Lofti
    https://stackoverflow.com/users/12349101/nordine-lotfi
    written by Thingamabobs
    https://stackoverflow.com/users/13629335/thingamabobs

    The infinite canvas allows you to have infinite space to draw.
    
    You can move around the world as follows:
    - MouseWheel for Y movement.

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

    MAX_ZOOM = 1.8
    MIN_ZOOM = 0.3

    def __init__(self, master, bg_color = 'black', **kwargs, ):
        super().__init__(master, **kwargs)

        self._x_pos         = 0     #viewed position in x direction
        self._y_pos         = 0     #viewed position in y direction
        self._xshifted      = 0     #view moved in x direction
        self._yshifted      = 0     #view moved in y direction
        self._zoom_val      = 1.0   #level of zoom
        self.origin         = self.create_oval(0, 0, 0, 0, fill='', outline='white')

        self.bg_color = bg_color
        try:
            self.configure(confine=False, highlightthickness=0, bd=0, background=self.bg_color)
        except:
            self.configure(confine=False, highlightthickness=0, bd=0, background='black')
        self.bind('<MouseWheel>',    self._scroll)

        return None

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

    def _update_indicators(self):
        for indicator in self.find_withtag('indicator'):
            self.delete(indicator)
        origin_c = self.coords(self.origin)
        x1, y1 = self.viewing_box_center()
        x2, y2 = -((x1 - origin_c[0]) * 0.01) , -((y1- origin_c[1]) * 0.01)
        dash = max(min(int(abs(x1/500)), 12), 1)
        self.indicator = self.create_line(x1, y1, x1 + x2, y1 + y2, fill='#8b8b8b', dash=(1, dash), width=1, tags='indicator')

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
        self._update_indicators()

    def _scroll(self,event):
        if event.state == 1:
            self._wheel_scroll('x', int(event.delta * 4.75 * min(max(self._zoom_val, 0.8), 1.4) ))
        elif event.state == 0:
            self._wheel_scroll('y', int(event.delta * 4.75 * min(max(self._zoom_val, 0.8), 1.4)) )
        elif event.state in [16, 17]:
            self._zoom(event)
    
    def _zoom(self, event):
        xorigin, yorigin = self.viewing_box_center()
        if event.delta < 0 and self._zoom_val <= self.MAX_ZOOM:
            self._zoom_val += 0.02
            self.scale('all', xorigin, yorigin, 0.9799, 0.9799)
        elif event.delta > 0 and self._zoom_val >= self.MIN_ZOOM:
            self._zoom_val -= 0.02
            self.scale('all', xorigin, yorigin, 1.0205, 1.0205)

def test():
    root = tk.Tk()
    root.geometry('1000x800')
    canvas = InfiniteCanvas(root)
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.create_rectangle(0, 0, 100, 100, fill='white')
    root.mainloop()

if __name__ == '__main__':
    test()