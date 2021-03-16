import numpy as np
from scipy.io import wavfile
from pylab import fft

from PIL import Image
import pdb

import matplotlib.pyplot as plt

import imageio

EPSILON=1e-20

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
        assert self.mfile is not None
        #much of the fft code was taken from http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
        sampFreq, snd = wavfile.read(self.mfile)
        s1=snd[:,0] #we only use the right channel (not the left one)
        if(snd.dtype=='int16'): s1=s1/(2.**15)
        
        # TODO first get the fft of the entire mfile (num_periods = 1)
        numpoints = len(s1)
        freqs2pow = sound2freqpower(s1)


        nUniquePts = int(np.ceil(numpoints + 1) / 2)
        freqlabels = np.arange(0,nUniquePts,1) * (sampFreq/numpoints)
        num_freq_per_buck = int(len(freqs2pow) / self.num_buck)

        def freq2buckind(freq):
            num = int(np.searchsorted(freqlabels,freq) // num_freq_per_buck)
            # just put all the remaining frequencies in the last bucket
            if num>=self.num_buck: return self.num_buck-1
            else: return num

        buckets = [sum(freqs2pow[
                        buck*num_freq_per_buck:
                        (buck+1)*num_freq_per_buck]) 
                    for buck in range(self.num_buck)]

        logbuckets = np.log(np.array(buckets))
        maxdb = logbuckets.max()

        # Now do fft for each screen
        num_samples_period = int(self.period * sampFreq)
        num_periods = len(s1)//num_samples_period

        for period_idx in range(num_periods):
            if(period_idx%10==0): print(str(period_idx)+" out of "+str(num_periods)+ " complete")
            sp = s1[period_idx*num_samples_period :
                    (period_idx+1)*num_samples_period]

            n_p = len(sp)
            nUniquePts_p = int(np.ceil(n_p + 1) / 2)

            freqs2pow_p = sound2freqpower(sp)
            
            freqlabels_p = np.arange(0,nUniquePts_p,1) * (sampFreq/n_p)

            #put frequencies in buckets
            freq2buckind_p = [freq2buckind(freq) for freq in freqlabels_p]
            # pdb.set_trace()

            changes = [ind for ind,buckind in enumerate(freq2buckind_p) 
                        if ind>0 and freq2buckind_p[ind]!=freq2buckind_p[ind-1]]
            changes.append(len(freq2buckind_p))

            buckets_p = [EPSILON for buck in range(self.num_buck)]

            for ind,ch in enumerate(changes):
                if ind==0: continue
                buckets_p[freq2buckind_p[ch-1]] = sum(freqs2pow_p[changes[ind-1]:ch])

            #convert list of buckets into a screen, using the space-filling curve
            screen = np.zeros((self.side_length,self.side_length))
            for bidx,bp in enumerate(buckets_p):
                screen[self.curve2plane(bidx)]=bp

            # TODO display the screen
            screen = np.log(screen) / maxdb
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
    ag = AnimGen(30,"data/Reflected.wav","test.gif",0.1)
    ag.gen_anim()