import os, sys
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

    M = np.zeros((xsteps,ysteps))

    hs = np.arange(0,50,bw)

    for step in path :
        idx, cell, loc = step
        kv = k.krige( data, m.spherical2, hs, bw, loc, 4 )
        M[ cell[0], cell[1] ] = kv
        newdata = [ loc[0], loc[1], kv ]
        data = np.vstack(( data, newdata ))
    return M


def read_data( fn ):
    f = open( fn, "r" )
    title = f.readline()
    nvar = int( f.readline() )
    columns = [ f.readline().strip() for i in range( nvar ) ]
    data = list()
    while True:
        line = f.readline()
        if line == '':
            break
        else:
            data.append( line )
    data = [ i.strip().split() for i in data ]
    data = np.array( data, dtype=np.float )
    df = pandas.DataFrame( data, columns=columns,  )
    return df
 
# Set up MPI environ
fname = sys.argv[1]
keys = ['uid','tid','rank','iter']
values = fname.split('_')
args = dict(zip(keys, values))
udir = 'app/users/{0}'.format(args['uid'])
res_dir = '{0}/results'.format(udir)

print "Init iteration: {}".format(args['iter'])

# Begin script
clstr = read_data( '/var/www/fastGIS/app/scripts/cluster.dat' )

nx = 50 ; xsteps = 3
ny = 50 ; ysteps = 3
xrng = np.linspace(0,nx,num=xsteps)
yrng = np.linspace(0,ny,num=ysteps)

N = xsteps * ysteps
idx = np.arange( N )
random.shuffle( idx )
path = list()
t = 0
for i in range( xsteps ):
    for j in range( ysteps ):
        path.append( [ idx[t], (i,j), (xrng[i],yrng[j]) ] )
        t += 1
path.sort()
locations = np.array( clstr[['Xlocation','Ylocation']] )
variable = np.array( clstr['Primary'] )
norm, inv, param, mu, sd = z.to_norm2( variable, 1000 )
data = np.vstack((locations.T,norm)).T

t0 = time.time()
M = sgs( data, 5, path, xsteps, ysteps )
t1 = time.time()
print "SGS Time:", (t1-t0)/60.0

# save output
save_path = os.path.join(res_dir, fname)
with open(save_path + '.pkl', 'wb') as out:
    pickle.dump(M, out, pickle.HIGHEST_PROTOCOL)

# create image, just for fun
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

savefig(save_path+'.png', fmt='png', dpi=200 )

print "Complete iteration: {}".format(args['iter'])
