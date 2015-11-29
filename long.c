#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <mpi.h>
#include <string.h>
#include <signal.h>

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

void stop_py(int signum) {
  printf("caught sig %d\n", signum);
}

int do_slave(int rank) {
  int pyfd[2], mpifd[2], nbytes;
  pid_t pid;
  char pybuff[MAX_BUFF], mpibuff[MAX_BUFF];
  
  // first, execute computation script
  if (pipe(pyfd) == -1)
    die("pipe");
  if ((pid=fork()) == -1)
    die("fork");
  
  if (pid == 0) {
    dup2(pyfd[1], STDOUT_FILENO);
    close(pyfd[0]); 
    close(pyfd[1]);
    execl("/var/www/fastGIS/venv/bin/python", "python",  "/var/www/fastGIS/bar.py", (char*)0 );
    die("execl");
  }
 
  close(pyfd[1]);
  // second, set up dedicated logger  
  if ((pid=fork()) == -1)
    die("fork");
  
  if (pid == 0) {
    signal(SIGUSR1, stop_py);

    while ((nbytes = read(pyfd[0], pybuff, MAX_BUFF)) > 0) {
      pybuff[nbytes] = '\0';
      printf("Python proc %d: %s\n", rank, pybuff);
    }
  } 
  // finally, let the parent of both processes receive MPI messages
  else {
    MPI_Status status;
    while (1) {
      MPI_Recv(&mpibuff, MAX_BUFF, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
      printf("Proc %d: %s\n", rank, mpibuff);
      if (strcmp(mpibuff, "sigusr") == 0) {
	kill(pid, SIGUSR1);
      }
    }
  }
}

int do_master() {
  char buff[MAX_BUFF];
  char *cptr;
  
  printf("Send a msg: \n");
  while (1) {
    fgets(buff, MAX_BUFF, stdin);
    if ( (cptr = strchr(buff, '\n')) != NULL) *cptr = '\0';
   
    MPI_Send(buff, strlen(buff) + 1, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
  }
}
