""" Tests for autocorrelogram"""

import os
os.environ['HOMESHARE'] = r'C:\temp\astropy'
import sys
sys.path.insert(1, os.path.join(os.getcwd(), '..'))

import inspect
import scipy.io as spio
import numpy as np
import pytest

from opexebo.analysis import angular_occupancy as func

print("=== tests_analysis_angular_occupancy ===")





###############################################################################
################                MAIN TESTS
###############################################################################

def test_angular_random_data():
    '''Doesn't test that meaningful results are produced, only that something is'''
    n = 1000
    time = np.arange(n)
    angles = np.random.rand(n)
    a, b, c = func(time, angles)
    print(f"{inspect.stack()[0][3]} passed")
    return True
    
def test_angular_zero_data():
    '''Doesn't test that meaningful results are produced, only that something is'''
    n = 1000
    time = np.arange(n)
    angles = np.zeros(n)
    a, b, c = func(time, angles)
    print(f"{inspect.stack()[0][3]} passed")
    return True
    


#if __name__ == '__main__':
#    test_angular_random_data()
#    test_angular_zero_data()
    
    