"""Provide a function for mapping a list of positional data into a 1D or 2D space"""


import numpy as np
from opexebo.general import validatekeyword__arena_size
import opexebo.defaults as default

def accumulatespatial(pos, **kwargs):
    """
    Accumulate repeated observations of a variable into a binned representation
    by means of a histogram. 
    
    
    Parameters
    ----------
    pos : np.ndarray
        Nx1 or Nx2 array of positions associated with z
        x = pos[0,:]
        y = pos[1,:]
        This matches the simplest input creation:
            pos = np.array( [x, y] )

   kwargs
        bin_width       : float. 
            Bin size (in cm). Bins are always assumed square default 2.5 cm.
        arena_size      : float or tuple of floats. 
            Dimensions of arena (in cm)
            For a linear track, length
            For a circular arena, diameter
            For a square arena, length or (length, length)
            For a non-square rectangle, (length1, length2)
            In this function, a circle and a square are treated identically.
        limits : tuple or np.ndarray
            (x_min, x_max) or (x_min, x_max, y_min, y_max)
            Provide concrete limits to the range over which the histogram searches
            Any observations outside these limits are discarded
            If no limits are provided, then use np.nanmin(data), np.nanmax(data)
            to generate default limits. 
            As is standard in python, acceptable values include the lower bound
            and exclude the upper bound
        
    
    
    
    Returns
    -------
    hist : np.ndarray
        1D or 2D histogram of the occurrences of the input observations
        Dimensions given by arena_size/bin_width
        Not normalised - each cell gives the integer number of occurrences of 
        the observation in that cell
    edges : :np.ndarray
        Array of bin edges used in calculating the histogram
        Either 1D or 2D. 
    
    
    See also
    --------
    BNT.+analyses.map
    
    """
    
    # Check correct inputs:
    dims, num_samples = pos.shape

    if dims not in (1,2):
        raise ValueError("pos should have either 1 or 2 dimensions. You have \
                         provided %d dimensions." % dims)

    
    # Get kwargs values
    bin_width = kwargs.get("bin_width", default.bin_width)
    arena_size = kwargs.get("arena_size")
    limits = kwargs.get("limits", None)
    if type(limits) not in (tuple, list, np.ndarray, type(None)):
        raise ValueError("You must provide an array-like 'limits' value, e.g. \
            (x_min, x_max, y_min, y_max). You provided type %s" % type(limits))
    
    
    arena_size, is_2d = validatekeyword__arena_size(arena_size, dims)
    num_bins = np.ceil(arena_size / bin_width)
    
    

        


    # Histogram of positions
    x = pos[0,:]
    
    if is_2d:
        y = pos[1,:]
        if limits == None:
            limits = ( [np.nanmin(x), np.nanmax(x)],
                         [np.nanmin(y), np.nanmax(y)] )
        elif len(limits) != 4:
            raise ValueError("You must provide a 4-element 'limits' value for a \
                             2D map. You provided %d elements" % len(limits))
        else:
            limits = ( [limits[0], limits[1]], # change from a 4 element list to a list of lists
                             [limits[2], limits[3]] )
        in_range = np.logical_and( np.logical_and(x>=limits[0][0], x<limits[0][1]),
                                    np.logical_and(y>=limits[1][0], y<limits[1][1]) )
        in_range_x = x[in_range]
        in_range_y = y[in_range]
        
        hist, xedges, yedges = np.histogram2d(in_range_x, in_range_y,
                                       bins=num_bins, range=limits)
        hist = hist.transpose() # Match the format that BNT traditionally used.
        edges = np.array([yedges, xedges]) # Note that due to the tranposition
                                            # the label xedge, yedge is potentially misleading
    else:
        if limits == None:
            limits = [np.nanmin(x), np.nanmax(x)]
        elif len(limits) != 2: 
            raise ValueError("You must provide a 2-element 'limits' value for a \
                             1D map. You provided %d elements" % len(limits))
            
        in_range = np.logical_and(x>=limits[0], x<limits[1])
        in_range_x = x[in_range]
        
        hist, edges = np.histogram(x, bins=num_bins, range=limits)
    
    
    return hist, edges