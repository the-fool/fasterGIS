import os, sys, random, pickle
from time import sleep
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fname = sys.argv[1]
keys = ['uid','tid','rank','iter']
values = fname.split('_')
args = dict(zip(keys, values))
udir = 'app/users/{0}'.format(args['uid'])
res_dir = '{0}/results'.format(udir)

print "Init iteration: {}".format(args['iter'])
sleep(random.randint(1,10))

from pylab import imshow, show, get_cmap, savefig
from numpy import random

save_path = os.path.join(res_dir, fname)
with open(save_path + '.pkl', 'wb') as out:
    pickle.dump(fname, out, pickle.HIGHEST_PROTOCOL)

Z = random.random((50,50))   # Test data

imshow(Z, cmap=get_cmap("Spectral"), interpolation='nearest')
show()
savefig(save_path+'.png', fmt='png', dpi=200 )


print "Complete iteration: {}".format(args['iter'])
