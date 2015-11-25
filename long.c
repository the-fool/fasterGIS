#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  printf("Init\n");
  int i = 0;
  for ( ; i++ < 10; ){
    sleep(1);
    printf("%d\n", i);
    fflush(stdout);
  }

}
