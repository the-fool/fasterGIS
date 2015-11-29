#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <mpi.h>
#define die(e) do { fprintf(stderr, "%s\n", e); exit(EXIT_FAILURE); } while (0);
#define MAX_BUFF 4096

int do_slave(int rank);
int do_master();

int main(int argc, char *argv[]) {

  int world_size, world_rank;

  MPI_Init(NULL, NULL);

  MPI_Comm_size(MPI_COMM_WORLD, &world_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

  if (world_rank == 0)
    do_master();
  else
    do_slave(world_rank);
 
  MPI_Finalize();
}

int do_slave(int rank) {
  int pfd[2], nbytes;
  pid_t pid;
  char buff[MAX_BUFF];
  
  if (pipe(pfd) == -1)
    die("pipe");
  
  if ((pid=fork()) == -1)
    die("fork");
  
  if (pid == 0) {
    dup2(pfd[1], STDOUT_FILENO);
    close(pfd[0]); 
    close(pfd[1]);
    execl("/var/www/fastGIS/venv/bin/python", "python",  "/var/www/fastGIS/bar.py", (char*)0 );
    die("execl");
  }else {
    close(pfd[1]);
    while ((nbytes = read(pfd[0], buff, sizeof(buff))) > 0) {
      buff[nbytes] = '\0';
      printf("Proc %d: %s\n", rank, buff);
    }
  }
}

int do_master() {

}
