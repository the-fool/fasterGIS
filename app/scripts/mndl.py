from PIL import Image
import time
import numpy
import sys, os, pickle

fname = sys.argv[1]
keys = ['uid','tid','rank','iter']
values = fname.split('_')
args = dict(zip(keys, values))
udir = 'app/users/{0}'.format(args['uid'])
res_dir = '{0}/results'.format(udir)

print "Init iteration: {}".format(args['iter'])

WIDTH = 500
HEIGHT = 500
MAX_ITER = 25

pix = numpy.zeros((HEIGHT, WIDTH, 3), dtype=numpy.uint8)

for y in xrange(0, HEIGHT):
    for x in xrange(0, WIDTH):
        zoom = 0.3
        real = (float(x) / float(WIDTH)) * (1.0 / zoom) + -2.1 
        imaginary = (float(y) / float(HEIGHT)) * (1.0 / zoom) + -1.6
        const_real = real
        const_imaginary = imaginary
        z2 = 0.0
        iter_count = 0
        for iter_loop in xrange(0, MAX_ITER):
            temp_real = real
            real = (temp_real * temp_real) - (imaginary * imaginary) + const_real
            imaginary = 2.0 * temp_real * imaginary + const_imaginary
            z2 = real * real + imaginary * imaginary

            iter_count = iter_loop
            if z2 > 4.0:
                break
        if z2 > 4.0:            
            c = iter_count * 10 % 255
            if c > 50:
                pix.itemset((y,x, 2), c)
            else:
                pix.itemset((y,x,2), 50)

save_path = os.path.join(res_dir, fname)
with open(save_path + '.pkl', 'wb') as out:
    pickle.dump(pix, out, pickle.HIGHEST_PROTOCOL)

mandelbrot = Image.fromarray(pix, 'RGB')
mandelbrot.save(save_path + ".png")

print "Complete iteration: {}".format(args['iter'])
