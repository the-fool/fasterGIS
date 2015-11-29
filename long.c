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
pid_t exec_script(int *pfd);
int manage_script(int rank);

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


int PAUSED = 0;

void stop_py(int signum) {
  printf("caught sig %d\n", signum);
  PAUSED = !PAUSED;
}

int do_slave(int rank) {
  pid_t pid;
  char pybuff[MAX_BUFF], mpibuff[MAX_BUFF];
  
  if ((pid=fork()) == -1)
    die("pipe");
  if (pid == 0) {
    manage_script(rank);
  } else {
    // MPI msg listener
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

int manage_script(int rank){
  int pfd[2], nbytes; 
  char buff[MAX_BUFF];
  pid_t pid;

  // first, execute computation script
  // second, set up dedicated logger  
  pid = exec_script(pfd);

  struct sigaction act;
  act.sa_handler = stop_py;
  sigemptyset(&act.sa_mask);
  act.sa_flags = 0;
  sigaction(SIGUSR1, &act, 0);
    
  while (!PAUSED) {
    while (!PAUSED && (nbytes = read(pfd[0], buff, MAX_BUFF)) > 0) {
      buff[nbytes] = '\0';
      printf("Python proc %d: %s\n", rank, buff);
    }
    //kill(pypid, SIGINT);
    pause();
  }
} 

pid_t exec_script(int *pfd) {
  pid_t pid;

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
  }
  close(pfd[1]);
  return pid;
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
