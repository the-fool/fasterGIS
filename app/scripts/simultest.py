import geostats.utilities as u
import geostats.kriging as k
import geostats.simulation as s
import geostats.zscoretrans as z
import geostats.model as m
from pylab import *
import scipy.interpolate
import numpy as np

# read cluster.dat
d = u.readGeoEAS("cluster.dat")
print d
# take the first three columns
d = d[:,:3]

# define the lags and tolerance 
# for the semivariogram modeling
lags, tol = np.linspace( 10, 50, 10 ), 5

# if the data is not normally distributed,
# perfrom a z-score transformation
d, inv = z.to_norm( d )

# perform sequential Gaussian simulation using
# a spherical model, on a 5x5 grid
mod = s.sgs( d, m.spherical, lags, tol, 5, 5 )

# use the [:,::-1].T to a) reverse the order of the columns
# and then b) transpose the data, this takes it from Python
# conventions, back to the way we normally think of spatial data
print mod[:,::-1].T

# assuming you have matplotlib and  pylab installed, 
# you can visulize the untransformed data
matshow( m[:,::-1].T, cmap=u.YPcmap )

# perform the back-transformation
n = u.from_norm( m, inv )

print n[:,::-1].T
