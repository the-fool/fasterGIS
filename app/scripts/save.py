import os, sys
from time import sleep

keys = ['uid','tid','rank','iter']
values = sys.argv[1].split('_')
args = dict(zip(keys, values))
print args
print "Init iter: {}".format(args['iter'])
sleep(1)
