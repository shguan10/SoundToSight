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
        self.size=size
        self.mfile=musicfile
        self.dfile = destfile
        self.freq=1./period #frequency of screen update
        self.anim=None #list of screens to display as animation,
                        #each screen is a 2d array of size^2
                            #and is a list of rows. so y is incremented fastest
                        #each pixel in a screen is a color
        self.anim_counter = 0 #index of curr screen

        #TODO generate screens based on frequency input
        #so we need to use fft

    def reset(self):
        self.anim_counter = 0

    def has_next(self):
        return self.anim_counter<len(self.anim)

    def get_next(self):
        """

        :return: next screen
        """
        if(not self.has_next()): return None
        r = self.anim[self.anim_counter]
        self.anim_counter+=1
        return r

    def curve2plane(self,index):
        """
        Get the coordinates of the point mapped to curve[index]
        :param index: the index of interest on the curve
        :return: coordinates on the plane. Integer Tuple (x,y)
        """
        #TODO try Hilbert Curve
        #iterates stuff in each row first. so y gets incremented fastest
        return (index/self.size,index%self.size)

    def plane2curve(self,coord):
        """
        Get the curve[index] mapped to the coordinates on the plane
        :param coord: the point of interest on the plane. Integer Tuple (x,y)
        :return: index on curve
        """
        #TODO use Hilbert Curve
        return coord[0]*self.size+coord[1]