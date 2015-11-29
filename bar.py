from time import sleep
import sys

i = 0
for i in range(15):
    sleep(1)
    print i, "here is a line"
    sys.stdout.flush()
