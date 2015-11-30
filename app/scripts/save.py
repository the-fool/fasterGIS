import os, sys
from time import sleep

fname = sys.argv[1]
keys = ['uid','tid','rank','iter']
values = fname.split('_')
args = dict(zip(keys, values))
udir = 'app/users/{0}'.format(args['uid'])
res_dir = '{0}/results'.format(udir)
print fname
print "Init iteration: {}".format(args['iter'])
f = open(os.path.join(res_dir, fname), 'w+')
f.write("r{0}i{1}".format(args['rank'], args['iter']))
sleep(1)
f.close()
print "Complete iteration: {}".format(args['iter'])
