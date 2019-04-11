# File: demopanels.py
# References:
#    http://hg.python.org/cpython/file/4e32c450f438/Lib/tkinter/simpledialog.py
#    http://docs.python.org/py3k/library/inspect.html#module-inspect
#
# Icons sourced from:
#    http://findicons.com/icon/69404/deletered?width=16#
#    http://findicons.com/icon/93110/old_edit_find?width=16#
#
# This file is imported by the Tkinter Demos

from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import Dialog
from PIL import Image
from PIL import ImageTk #Instal by sudo apt-get install python3-pil.imagetk
import inspect


class MsgPanel(ttk.Frame):
    def __init__(self, master, msgtxt,row = 0 ,column = 0):
        ttk.Frame.__init__(self, master)
        self.grid(row=row,column=column)

        msg = Label(self, wraplength='4i', justify=LEFT)
        msg['text'] = ''.join(msgtxt)
        msg.pack(fill=X, padx=0, pady=5)


class SeeDismissPanel(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.pack(side=BOTTOM, fill=X)  # resize with parent

        # separator widget
        sep = ttk.Separator(orient=HORIZONTAL)

        # Dismiss button
        im = Image.open('images//delete.png')  # image file
        imh = ImageTk.PhotoImage(im)  # handle to file
        dismissBtn = ttk.Button(text='Dismiss', image=imh, command=self.winfo_toplevel().destroy)
        dismissBtn.image = imh  # prevent image from being garbage collected
        dismissBtn['compound'] = LEFT  # display image to left of label text

        # 'See Code' button
        im = Image.open('images//view.png')
        imh = ImageTk.PhotoImage(im)
        codeBtn = ttk.Button(text='See Code', image=imh, default=ACTIVE, command=lambda: CodeDialog(self.master))
        codeBtn.image = imh
        codeBtn['compound'] = LEFT
        codeBtn.focus()

        # position and register widgets as children of this frame
        sep.grid(in_=self, row=0, columnspan=4, sticky=EW, pady=5)
        codeBtn.grid(in_=self, row=1, column=0, sticky=E)
        dismissBtn.grid(in_=self, row=1, column=1, sticky=E)

        # set resize constraints
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # bind <Return> to demo window, activates 'See Code' button;
        # <'Escape'> activates 'Dismiss' button
        self.winfo_toplevel().bind('<Return>', lambda x: codeBtn.invoke())
        self.winfo_toplevel().bind('<Escape>', lambda x: dismissBtn.invoke())