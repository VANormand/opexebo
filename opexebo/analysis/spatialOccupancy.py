'''
Provides function to calculate the spatial occupancy of the arena
'''
import numpy as np
import opexebo
from opexebo import defaults as default



def spatial_occupancy(time, position, speed, **kwargs):
    '''
    Generate an occpuancy map: how much time the animal spent in each location
    in the arena.    
    
    NOTES: This assumes that the positions have already been aligned and curated
    to remove NaNs. This is based on the expectation that it will primarily be 
    used within the DataJoint framework, where the curation takes place at a 
    much earlier stage.
    
    Parameters
    ----------
    time       : ndarray
        [t] timestamps of position and speed data
    position   : ndarray. 
        [x, y] or [x]. [0,:] -> xThis matches array creation 
        with positions=np.array([x, y])
    speed       : ndarray. 
        [s]
    
    kwargs
        arena_shape : str
            accepts: ("square", "rectangle", "rectangular", "rect", "s", "r")
                    ("circ", "circular", "circle", "c")
                    ("linear", "line", "l")
            Rectangular and square are equivalent. Elliptical or n!=4 polygons
            not currently supported. Defaults to Rectangular
        arena_size      : float or tuple of floats. 
            Dimensions of arena (in cm)
            For a linear track, length
            For a circular arena, diameter
            For a square arena, length or (x_length, y_length)
            For a non-square rectangle, (x_length, y_length)
            In this function, a circle and a square are treated identically.
        bin_width       : float. 
            Bin size (in cm). Bins are always assumed square default 2.5 cm.
        speed_cutoff    : float. 
            Timestamps with instantaneous speed beneath this value are ignored. 
            Default 0
        limits : tuple or np.ndarray
            (x_min, x_max) or (x_min, x_max, y_min, y_max)
            Provide concrete limits to the range over which the histogram searches
            Any observations outside these limits are discarded
            If no limits are provided, then use np.nanmin(data), np.nanmax(data)
            to generate default limits. 
            As is standard in python, acceptable values include the lower bound
            and exclude the upper bound
        debug           : bool
            If true, print out debugging information throughout the function.
            Default False
    
    Returns
    -------
    masked_map : np.ma.MaskedArray
        Unsmoothed map of time the animal spent in each bin.
        Bins which the animal never visited are masked (i.e. the mask value is 
        True at these locations)
    coverage : float
        Fraction of the bins that the animal visited. In range [0, 1]
    bin_edges : list-like
        x, or (x, y), where x, y are 1d np.ndarrays
        Here x, y correspond to the output histogram
    
    
    See also
    --------
    BNT.+analyses.map
        
    Copyright (C) 2019 by Simon Ball

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    '''
    # Check for correct shapes. 
    dimensionality, num_samples = position.shape
    if dimensionality not in (1, 2):
        raise ValueError("Positions array has the wrong number of columns (%d)" % dimensionality)
    if speed.ndim != 1:
        raise ValueError("Speed array has the wrong number of columns")
    if speed.size != num_samples:
        raise ValueError("Speed array does not have the same number of samples as Positions")    
    if "arena_size" not in kwargs:
        raise KeyError("Arena dimensions not provided. Please provide dimensions using keyword 'arena_size'.")
    
    
    # Handle NaN positions by converting to a Masked Array
    position = np.ma.masked_invalid(position)
    
    
    speed_cutoff = kwargs.get("speed_cutoff", default.speed_cutoff)
    debug = kwargs.get("debug", False)
    


    
    if debug:
        print("Number of time stamps: %d" % len(time))
        print("Maximum time stamp value: %.2f" % time[-1])
        print("Time stamp delta: %f" % np.min(np.diff(time)))
   

    good = speed>speed_cutoff
    x = position[0,:][good]
    y = position[1,:][good]
    pos = np.array([x,y])
    
    occupancy_map, bin_edges = opexebo.general.accumulate_spatial(pos, **kwargs)
    if debug:
        print("Frames included in histogram: %d (%.3f)" % (np.sum(occupancy_map), np.sum(occupancy_map)/len(time)) )

    # So far, times are expressed in units of tracking frames
    # Convert to seconds:
    frame_duration = np.min(np.diff(time))    
    occupancy_map_time = occupancy_map * frame_duration
    
    if debug:
        print("Time length included in histogram: %.2f (%.3f)" % (np.sum(occupancy_map_time), np.sum(occupancy_map_time)/time[-1]) )
    

    masked_map = np.ma.masked_where(occupancy_map < 0.001, occupancy_map_time)
    
    # Calculate the fractional coverage based on the mask. The occupancy_map is
    # zero where the animal has not gone, and therefore non-zero where the animal
    # HAS gone. . Coverage is 1.0 when the animal has visited every location
    # Does not take account of a circular arena, where not all locations are
    # accessible
    
    arena_size = kwargs.get("arena_size")
    bin_width = kwargs.get("bin_width", default.bin_width)
    shape = kwargs.get("arena_shape", default.shape)
    
    if shape.lower() in default.shapes_square:
        coverage = np.count_nonzero(occupancy_map) / occupancy_map.size
    elif shape.lower() in default.shapes_circle:
        if type(arena_size) in (float, int):
            radius = arena_size / 2
        elif type(arena_size) in (tuple, list, np.ndarray):
            radius = arena_size[0]/2
        x_centres = bin_edges[0][:-1] + (bin_width / 2)
        y_centres = bin_edges[1][:-1] + (bin_width / 2)
        X, Y = np.meshgrid(x_centres, y_centres)
        distance_map = np.sqrt(np.power(X,2) + np.power(Y,2))
        in_field = distance_map<=radius
        
        coverage = min(1.0, np.count_nonzero(occupancy_map) / (np.sum(in_field)))
            # Due to the thresholding, coverage might be calculated to be  > 1
            # In this case, cut off to a maximum value of 1.
    elif shape.lower() in default.shapes_linear:
        raise NotImplementedError("Spatial Occupancy does not currently"
                                  " support linear arenas")
    else:
        raise NotImplementedError(f"Arena shape '{shape}' not understood")
    
    return masked_map, coverage, bin_edges
    
    
     
