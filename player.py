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

        if(self.mfile!=None):
            self.mixer = mixer
            self.mixer.init()
            self.mixer.music.load(self.mfile)

        self.period = period
        self.animgen = AnimGen(self.size, self.mfile, "data\\test",self.period)
        self.animgen.gen_anim()

        print('before reset')
        self.reset()
        print("after reset")
        self.oktoplay=True

    def showInfo(self):
        #TODO implement
        pass

    def play(self):
        if(self.mfile!=None): self.mixer.music.play()
        #self.display_next_screen()
        """"""
        while(self.animgen.has_next() and self.oktoplay):
            #print("here")
            #TODO This method to play the animation is too slow
            self.display_next_screen()
            sleep(self.period)
        """"""

    def reset(self):
        if(self.mfile!=None): self.mixer.stop()
        self.oktoplay=False

        self.canvas.delete(tk.ALL)
        self.animgen.reset()
        print("before display")
        self.display_next_screen()
        print('after display')

        self.oktoplay=True

    def display_next_screen(self):
        screen = self.animgen.get_next() #list of rows, so y gets incremented first
        if(screen==None): raise IndexError
        self.canvas.delete(tk.ALL)
        for x in xrange(len(screen)):
            for y in xrange(len(screen)):
                psize= 1
                self.canvas.create_rectangle(x-psize,y+psize,x+psize,y-psize,fill=screen[x][y],width=0)

def main():
    root = tk.Tk()
    musicfile = "data\\Reflected.wav"
    #app = Player(root,musicfile,3) #TODO tweak the wait period here
    app = Player(root,None,.05) #TODO tweak the wait period here
    root.mainloop()

if __name__=="__main__":
    main()