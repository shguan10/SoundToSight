import numpy as np
from scipy.io import wavfile
from pylab import fft


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
    nUniquePts = int(np.ceil((len(samps) + 1) / 2.0))
    p = abs(fft(samps)[0:nUniquePts])
    p = p / float(len(samps))  # scale by the number of points so that
    # the magnitude does not depend on the length
    # of the signal or on its sampling frequency
    p = p ** 2  # square it to get the power
    # multiply by two (see technical document for details)
    # odd nfft excludes Nyquist point
    if len(samps) % 2 > 0:  # we've got odd number of points fft
        p[1:len(p)] = p[1:len(p)] * 2
    else:
        p[1:len(p) - 1] = p[1:len(p) - 1] * 2  # we've got even number of points fft
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
        self.num_buck = self.side_length ** 2 #number of buckets of rms power, to be converted into greyscale intensity
        self.mfile=musicfile
        self.dfile = destfile

        self.period= period #period between screen updates
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
            self.screens=[[[power2color(y+k,self.side_length+k) for y in xrange(self.side_length)] for x in xrange(self.side_length)]for k in xrange(100)]
        else:
            #much of the fft code was taken from http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
            sampFreq, snd = wavfile.read(self.mfile)
            s1=snd[:,0] #we only use the right channel
            if(snd.dtype=='int16'): s1=s1/(2.**15)
            #how many samples per period?
            num_samples_period = int(self.period * sampFreq)

            num_periods = len(s1)/num_samples_period

            """
            #get total power
            tp=sound2freqpower(s1)
            if((tp<0).any()):
                print("Something went wrong: some of the terms in tp are negative!")
                raise ValueError
            total_power = np.sqrt(np.sum(tp))
            """
            #for each period (screen)
            period_idx = 0
            while(period_idx<num_periods):
                if(period_idx!=0 and period_idx%10==0): print(str(period_idx)+" out of "+str(num_periods)+ " complete")
                #TODO this is slow because it makes a copy of the subarray
                p = sound2freqpower(s1[period_idx*num_samples_period :
                    (period_idx+1)*num_samples_period])
                #TODO apparently there might be frequencies that are present in a sub sample that are not present in the total sample?
                """
                if(np.sqrt(np.sum(p))>total_power):
                    print("Something went wrong: the power of a sub sample is larger than the total power")
                    print("period index: "+str(period_idx))
                    print("num_samples_period: "+str(num_samples_period))
                    raise ValueError
                """
                #put frequencies in buckets
                num_freq_bucket = len(p)/self.num_buck

                buckets = [0 for x in xrange(self.num_buck)] #contains rms of frequencies in each buckets
                numnonzero = 0
                bucket_idx = 0
                while(bucket_idx<self.num_buck):
                    #get rms of those frequencies
                    sum = 0
                    freq_idx = bucket_idx*num_freq_bucket
                    while(freq_idx<num_freq_bucket):
                        sum+=p[freq_idx]
                        freq_idx+=1
                    if(sum>0):numnonzero+=1
                    buckets[bucket_idx]=np.sqrt(sum)
                    #if(buckets[bucket_idx]>0): numnonzero+=1
                    bucket_idx+=1
                if((p>0).any()):
                    print(numnonzero>0)

                #convert list of buckets into a screen, using the space-filling curve
                screen = [[0 for y in xrange(self.side_length)] for x in xrange(self.side_length)]
                for bidx in xrange(len(buckets)):
                    (x,y)=self.curve2plane(bidx)
                    #color= power2color(buckets[bidx],total_power) #convert rms into greyscale
                    color= power2color(buckets[bidx],.5) #convert rms into greyscale
                    screen[x][y]=color
                period_idx+=1
                self.screens.append(screen)
        self.screen_index = 0
        print("Finished Animation with " + str(len(self.screens)) + " screens")

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
        return (index / self.side_length, index % self.side_length)

    def plane2curve(self,coord):
        """
        Get the curve[index] mapped to the coordinates on the plane
        :param coord: the point of interest on the plane. Integer Tuple (x,y)
        :return: index on curve
        """
        #TODO use Hilbert Curve
        return coord[0]*self.side_length + coord[1]