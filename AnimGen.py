import numpy as np
from scipy.io import wavfile
from pylab import fft

from PIL import Image
import pdb

import matplotlib.pyplot as plt

import imageio

def power2color(bucket_power,total_power):
    """
    :return: the string representation of the intensity
    """
    # convert to [0,256)
    if(bucket_power>total_power): raise ValueError
    val = int(bucket_power/float(total_power)*256) #TODO this always returns 0?
    #if(val>0 and val<200): val +=50
    return int2color(255-val) #we want higher values to be darker

def int2color(val):
    """
    returns string representation of color
    :param val: must be in [0,256)
    """
    if(val>=256 or val<0):
        print(val)
        raise ValueError
    s=hex(val)
    if(len(s)==3):
        s=s[2]+"0"
    elif(len(s)==4):
        s=s[2:]
    else: raise ValueError
    res="#"+s*3
    #print(res)
    return res

def sound2freqpower(samps):
    n = len(samps)
    p = fft(samps)

    nUniquePts = int(np.ceil(n + 1) / 2)
    
    p = p[:nUniquePts]
    p = abs(p)

    # now we normalize so that the magnitude is invariant on the number of points
    p = p / n

    # square it to get the power
    p = p ** 2  

    # multiply by two (see technical document for details)
    # odd nfft excludes Nyquist point
    if n % 2:  
        # we've got odd number of points fft
        p[1:len(p)] = p[1:len(p)] * 2
    else:
        p[1:len(p) - 1] = p[1:len(p) - 1] * 2

    return p

class AnimGen:
    """
    AnimGen creates an animation to be played alongside the music
    """
    def __init__(self,size,musicfile,destfile,period):
        """
        :param size: side length of the square plane. Integer
        :param musicfile: the musicfile to be converted
        :param destfile: the destination of the output video
        """
        self.side_length=size
        
        #number of frequency buckets
        # TODO if the number of buckets is greater than the number of frequencies then undesirable things happen
        self.num_buck = self.side_length * self.side_length 
        self.mfile=musicfile
        self.dfile = destfile

        self.period= period #period between screen updates, in seconds
        self.screens=[] #list of screens to display as animation,
                        #each screen is a 2d array of size^2
                            #and is a list of rows. so y is incremented fastest
                        #each pixel in a screen is a color (str)
        self.screen_index = -1 #index of curr screen

        #TODO generate screens based on frequency input
        #so we need to use fft
        #http://samcarcagno.altervista.org/blog/basic-sound-processing-python/

    def gen_anim(self):
        print("Generating Animation from audio file: "+str(self.mfile))

        if(self.mfile==None):
            #TODO write code to debug the player
            self.screens=[
                [
                    [power2color(y+k,self.side_length+k) 
                        for y in range(self.side_length)] 
                    for x in range(self.side_length)]
                for k in range(100)]
        else:
            #much of the fft code was taken from http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
            sampFreq, snd = wavfile.read(self.mfile)
            s1=snd[:,0] #we only use the right channel (not the left one)
            if(snd.dtype=='int16'): s1=s1/(2.**15)
            
            # TODO first get the fft of the entire mfile (num_periods = 1)
            numpoints = len(s1)
            self.period = numpoints / sampFreq

            #how many samples per period?
            num_samples_period = int(self.period * sampFreq)

            num_periods = len(s1)/num_samples_period


            #for each period (screen)
            period_idx = 0
            while(period_idx<num_periods):
                if(period_idx!=0 and period_idx%10==0): print(str(period_idx)+" out of "+str(num_periods)+ " complete")
                #TODO this is slow because it makes a copy of the subarray
                freqs2pow = sound2freqpower(s1[period_idx*num_samples_period :
                    (period_idx+1)*num_samples_period])
                
                #put frequencies in buckets
                # TODO the frequency buckets should not change from screen to screen
                
                num_freq_per_buck = int(len(freqs2pow) / self.num_buck)
                # pdb.set_trace()
                buckets = [
                    sum(freqs2pow[buck*num_freq_per_buck:(buck+1)*num_freq_per_buck]) 
                    for buck in range(self.num_buck)]

                #convert list of buckets into a screen, using the space-filling curve
                screen = np.zeros((self.side_length,self.side_length))
                for bidx in range(len(buckets)):
                    # color= power2color(buckets[bidx],screen_power) #convert rms into greyscale
                    screen[self.curve2plane(bidx)]=buckets[bidx]

                period_idx+=1
                # TODO display the screen
                # pdb.set_trace()
                screen /= screen.max()
                screen *= 255
                screen = np.uint8(screen)
                img = Image.fromarray(screen,'L')
                # img.show()

                self.screens.append(screen)
        self.screen_index = 0
        print("Finished Animation with " + str(len(self.screens)) + " screens")

        imageio.mimwrite(self.dfile,self.screens,duration=self.period)



    def reset(self):
        self.screen_index = 0

    def has_next(self):
        return 0<= self.screen_index < len(self.screens)

    def get_next(self):
        """
        :return: next screen
        """
        if(not self.has_next()): return None
        r = self.screens[self.screen_index]
        self.screen_index+=1
        return r

    def curve2plane(self,index):
        """
        Get the coordinates of the point mapped to curve[index]
        :param index: the index of interest on the curve
        :return: coordinates on the plane. Integer Tuple (x,y)
        """
        #TODO try Hilbert Curve
        #iterates stuff in each row first. so y gets incremented fastest
        return (index // self.side_length, index % self.side_length)

    def plane2curve(self,coord):
        """
        Get the curve[index] mapped to the coordinates on the plane
        :param coord: the point of interest on the plane. Integer Tuple (x,y)
        :return: index on curve
        """
        #TODO use Hilbert Curve
        return coord[0]*self.side_length + coord[1]


if __name__ == '__main__':
    ag = AnimGen(30,"data/Reflected.wav","test.gif",None)
    ag.gen_anim()