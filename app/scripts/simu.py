import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pickle
import time
import numpy as np
import scipy.stats
import scipy.optimize
import scipy.interpolate
import pandas

from pylab import *
from geostats import krige as k 
from geostats import kriging
from geostats import utilities
from geostats import zscoretrans as z 
from geostats import model as m
import random
def sgs( data, bw, path, xsteps, ysteps ):
    '''
    Input:  (data)   <N,3> NumPy array of data
            (bw)     bandwidth of the semivariogram
            (path)   randomized path through region of interest
            (xsteps) number of cells in the x dimension
            (ysteps) number of cells in the y dimension
    Output: (M)      <xsteps,ysteps> NumPy array of data
                     representing the simulated distribution
                     of the variable of interest 
    '''
    # create array for the output
    M = np.zeros((xsteps,ysteps))
    # generate the lags for the semivariogram
    hs = np.arange(0,50,bw)
    # for each cell in the grid..
    print len(path)
    for step in path :
        # grab the index, the cell address, and the physical location
        idx, cell, loc = step
        # perform the kriging
     
        kv = k.krige( data, m.spherical2, hs, bw, loc, 4 )
        # add the kriging estimate to the output
        M[ cell[0], cell[1] ] = kv
        # add the kriging estimate to a spatial location
        newdata = [ loc[0], loc[1], kv ]
        # add this new point to the data used for kriging
        data = np.vstack(( data, newdata ))
    return M


def read_data( fn ):
    f = open( fn, "r" )
    # title of the data set
    title = f.readline()
    # number of variables
    nvar = int( f.readline() )
    # variable names
    columns = [ f.readline().strip() for i in range( nvar ) ]
    # make a list for the data
    data = list()
    # for each line of the data
    while True:
        # read a line
        line = f.readline()
        # if that line is empty
        if line == '':
    
            break
    
        else:
            data.append( line )
    # strip off the newlines, and split by whitespace
    data = [ i.strip().split() for i in data ]
    # turn a list of list of strings into an array of floats
    data = np.array( data, dtype=np.float )
    # combine the data with the variable names into a DataFrame
    df = pandas.DataFrame( data, columns=columns,  )
    return df
 

clstr = read_data( '/var/www/fastGIS/app/scripts/cluster.dat' )

# we want 30 steps between 0 and 50, in both dimensions
nx = 50 ; xsteps = 15
ny = 50 ; ysteps = 15
xrng = np.linspace(0,nx,num=xsteps)
yrng = np.linspace(0,ny,num=ysteps)

# total number of cells
N = xsteps * ysteps
 
# an array of values 0 to N-1
idx = np.arange( N )
 
# randomize idx in place
random.shuffle( idx )
 
# create a list named path
path = list()
 
# initialize an index for idx
t = 0
 
# walk through the 2D grid..
for i in range( xsteps ):
    for j in range( ysteps ):
         
        # the first element is the shuffled index,
        # then the cell address, then the physical location
        path.append( [ idx[t], (i,j), (xrng[i],yrng[j]) ] )
         
        # increment the index
        t += 1
 
# sort the shuffled index, shuffling the cell 
# addresses and the physical locations (in feet)
path.sort()

# x and y coordinates in feet
locations = np.array( clstr[['Xlocation','Ylocation']] )
 
# value of the variable of interest, e.g., porosity or permeability
variable = np.array( clstr['Primary'] )
 
# the z-score transformation
norm, inv, param, mu, sd = z.to_norm2( variable, 1000 )
 
# the data to be kriged and appended to
# during the sequential Gaussian simulation
data = np.vstack((locations.T,norm)).T
 
t0 = time.time()
print "To sgs"
M = sgs( data, 5, path, xsteps, ysteps )
print "Post sgs"
t1 = time.time()
print (t1-t0)/60.0

with open('plot.pkl', 'wb') as out:
    pickle.dump(M, out, pickle.HIGHEST_PROTOCOL)

print "Pickled"

cdict = {'red':   ((0.0, 1.0, 1.0),
                   (0.5, 225/255., 225/255. ),
                   (0.75, 0.141, 0.141 ),
                   (1.0, 0.0, 0.0)),
         'green': ((0.0, 1.0, 1.0),
                   (0.5, 57/255., 57/255. ),
                   (0.75, 0.0, 0.0 ),
                   (1.0, 0.0, 0.0)),
         'blue':  ((0.0, 0.376, 0.376),
                   (0.5, 198/255., 198/255. ),
                   (0.75, 1.0, 1.0 ),
                   (1.0, 0.0, 0.0)) }
 
my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
matshow( M[:,::-1].T, cmap=my_cmap )
colorbar();
xs, ys = str(xsteps), str(ysteps)
xlabel('X') ; ylabel('Y') ; title('Raw SGS '+xs+'x'+ys+'\n')
savefig( 'sgs_untransformed_'+xs+'_by_'+ys+'.png', fmt='png', dpi=200 )
