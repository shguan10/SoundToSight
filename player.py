from time import sleep

from pygame import mixer
import sys
import Tkinter as tk
from AnimGen import AnimGen

class Player:
    def __init__(self,master,musicfile,period):
        self.master=master

        master.title("Sound to Sight")
        frame=tk.Frame(master)
        frame.pack()

        frame1=tk.Frame(frame)
        frame1.pack(side=tk.TOP)
        frame2=tk.Frame(frame)
        frame2.pack(side=tk.TOP)

        self.play_button = tk.Button(frame1, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT)
        self.resetButton=tk.Button(frame1,text="Reset",command=self.reset)
        self.resetButton.pack(side=tk.LEFT)
        self.infoButton = tk.Button(frame1,text="Help",command=self.showInfo)
        self.infoButton.pack(side=tk.LEFT)

        if(len(sys.argv)>1):
            self.size = int(sys.argv[1])
        else:
            self.size = 256

        self.canvas = tk.Canvas(frame2, width=self.size, height=self.size)
        self.canvas.pack(anchor=tk.CENTER)

        self.mfile = musicfile
        self.mixer = mixer
        self.mixer.init()
        self.mixer.music.load(self.mfile)

        self.period = period
        self.animgen = AnimGen(self.size, self.mfile, "data\\test",self.period)

        self.reset()

    def showInfo(self):
        #TODO implement
        pass

    def play(self):
        self.mixer.music.play()
        while(self.animgen.has_next()):
            self.display_next_screen()
            sleep(self.period)

    def reset(self):
        self.mixer.stop()
        self.canvas.delete(tk.ALL)
        self.animgen.reset()
        self.display_next_screen()

    def display_next_screen(self):
        screen = self.animgen.get_next() #list of rows, so y gets incremented first
        if(screen==None): raise IndexError
        for x in xrange(len(screen)):
            for y in xrange(len(screen)):
                psize= 1
                self.canvas.create_rectangle(x-psize,y+psize,x+psize,y-psize,fill=screen[x][y])

def main():
    root = tk.Tk()
    musicfile = "data\\rhapsodyinblue.mp3"
    app = Player(root,musicfile)
    root.mainloop()

if __name__=="__main__":
    main()