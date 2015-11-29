#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <mpi.h>
#include <string.h>
#include <signal.h>

#define die(e) do { fprintf(stderr, "%s\n", e); exit(EXIT_FAILURE); } while (0);
#define MAX_BUFF 4096

int do_slave(int rank, int iterations);
int do_master();
pid_t exec_script(int *pfd);
int manage_script(int rank, int iterations);

int main(int argc, char *argv[]) {

  int comm_size, comm_rank;

  MPI_Init(NULL, NULL);

  MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &comm_rank);

  if (comm_rank == 0)
    do_master();
  else
    do_slave(comm_rank, 1);
 
  MPI_Finalize();
}


int DORMANT = 0;
void go_dormant(int signum) {
  DORMANT = !DORMANT;
  printf("caught sig %d, d=%d\n", signum, DORMANT);
}

int do_slave(int rank, int iterations) {
  pid_t pid;
  char buff[MAX_BUFF];
  
  if ((pid=fork()) == -1)
    die("pipe");
  if (pid == 0) {
    manage_script(rank, iterations);
  } else {
    // MPI msg listener
    MPI_Status status;
    while (1) {
      MPI_Recv(&buff, MAX_BUFF, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
         
      if (strcmp(buff, "sigusr") == 0) {
	kill(pid, SIGUSR1);
      }
    }
  }
}

// to balance load with potentially many MPI processes,
// nodes may go dormant, where they kill their computation,
// but may begin computing agoin

int manage_script(int rank, int iterations){
  int pfd[2], nbytes, i=0; 
  char buff[MAX_BUFF];
  pid_t pid;

  struct sigaction act;
  act.sa_handler = go_dormant;
  sigemptyset(&act.sa_mask);
  act.sa_flags = 0;
  sigaction(SIGUSR1, &act, 0);
  
  while (!DORMANT && (i++ < iterations) ) {
    pid = exec_script(pfd); 
    while (!DORMANT && (nbytes = read(pfd[0], buff, MAX_BUFF)) > 0) {
      buff[nbytes] = '\0';
      printf("Proc %d: %s", rank, buff);
    } 
    close(pfd[0]);
    // check if EOF or SIGUSR1
    if (nbytes !=0) {
      kill(pid, SIGINT);
      waitpid(pid, NULL, 0);
      pause();
    } else {
      waitpid(pid, NULL, 0);
    }
  }
} 

pid_t exec_script(int *pfd) {
  pid_t pid;
 
  fflush(stdout);
 
 if (pipe(pfd) == -1)
    die("pipe");
  if ((pid=fork()) == -1)
    die("fork");
  if (pid == 0) {
    signal(SIGUSR1, SIG_DFL);
    dup2(pfd[1], STDOUT_FILENO);
    close(pfd[0]); 
    close(pfd[1]);
    execl("/var/www/fastGIS/venv/bin/python", "python",  "/var/www/fastGIS/app/scripts/bar.py", (char*)0 );
    die("execl");
  }
  close(pfd[1]);
  return pid;
}


int do_master() {
  char buff[MAX_BUFF];
  char *cptr;
  
  while (1) {
    fgets(buff, MAX_BUFF, stdin);
    if ( (cptr = strchr(buff, '\n')) != NULL) *cptr = '\0';
   
    MPI_Send(buff, strlen(buff) + 1, MPI_CHAR, 1, 0, MPI_COMM_WORLD);
    }
}
