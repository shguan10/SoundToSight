class AnimGen:
    """
    AnimGen creates an animation to be played alongside the music
    """
    def __init__(self,size,musicfile,destfile):
        """

        :param size: side length of the square plane. Integer
        :param musicfile: the musicfile to be converted
        :param destfile: the destination of the output video
        """
        self.size=size
        self.mfile=musicfile
        self.dfile = destfile
        self.anim=None

    def curve2plane(self,index):
        """
        Get the coordinates of the point mapped to curve[index]
        :param index: the index of interest on the curve
        :return: coordinates on the plane. Integer Tuple (x,y)
        """
        #TODO try Hilbert Curve
        #iterates stuff in each row first
        return (index/self.size,index%self.size)

    def plane2curve(self,coord):
        """
        Get the curve[index] mapped to the coordinates on the plane
        :param coord: the point of interest on the plane. Integer Tuple (x,y)
        :return: index on curve
        """
        #TODO use Hilbert Curve
        return coord[0]*self.size+coord[1]