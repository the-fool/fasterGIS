#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <mpi.h>
#include <string.h>
#include <signal.h>

#define die(e) do { fprintf(stderr, "%s\n", e); exit(EXIT_FAILURE); } while (0);
#define MAX_BUFF 4096


typedef struct {
  int iters;
  int uid;
  char tid[128];
  char type[64];
  char path[128];
} META;

int do_master(int comm_size);
int do_slave(int rank, META m);
int manage_script(int rank, META m);
pid_t exec_script(int *pfd, char *fname, char *type);

int main(int argc, char *argv[]) {

  int comm_size, comm_rank;
  MPI_Init(&argc, &argv);

  MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &comm_rank);

  
  META meta;
  meta.uid = atoi(argv[1]);
  strncpy(meta.tid, argv[2], strlen(argv[2]));
  strncpy(meta.type, argv[4], strlen(argv[4]));
  meta.iters = atoi(argv[3]) / (comm_size - 1);

  // divy the remaining iterations
  int i = 1;
  for (; i <= (atoi(argv[3]) % (comm_size - 1)); i++) {
    if (comm_rank == i)
      meta.iters++;
  }

  if (comm_rank == 0) {
    do_master(comm_size);
  }
  else {
     do_slave(comm_rank, meta);
  }
  fflush(stdout);
  MPI_Finalize();
}


int DORMANT = 0, SHUTDOWN=0;
void go_dormant(int signum) {
  DORMANT = !DORMANT;
}
void terminate(int signum) {
  SHUTDOWN = 1;
}

int do_slave(int rank, META meta) {
  pid_t pid;
  char buff[MAX_BUFF];
  
  if ((pid=fork()) == -1)
    die("fork");
  if (pid == 0) {
    manage_script(rank, meta);
  } 
  else {
    
    // MPI msg listener
    MPI_Status status;
    while (1) {
      MPI_Recv(&buff, MAX_BUFF, MPI_CHAR, 0, 0, MPI_COMM_WORLD, &status);
      printf("P%d: RECV: %s\n", rank, buff);   
      fflush(stdout);
      if (strcmp(buff, "PAUSE") == 0) {
	kill(pid, SIGUSR1);
      }
      else if (strcmp(buff, "SHUTDOWN") == 0) {
	kill(pid, SIGUSR2);
	wait();
	break;
      }
      else if (strcmp(buff, "FINISHED") == 0) {
	wait();
	printf("P%d: COLLECTED CHILD\n", rank);
	break;
      }
    }
  }
}

// to balance load with potentially many MPI processes,
// nodes may go dormant, where they kill their computation,
// but may begin computing again

int manage_script(int rank, META meta){
  int pfd[2], nbytes, i=0; 
  char buff[MAX_BUFF], fname[256];
  pid_t pid;

  struct sigaction dormant, shutdown;
  dormant.sa_handler = go_dormant;
  shutdown.sa_handler = terminate;
  sigemptyset(&dormant.sa_mask);
  sigemptyset(&shutdown.sa_mask);
  dormant.sa_flags = 0;
  shutdown.sa_flags = 0;
  sigaction(SIGUSR1, &dormant, 0);
  sigaction(SIGUSR2, &shutdown, 0);

  while (!DORMANT && !SHUTDOWN && (i++ < meta.iters) ) {
    printf("P%d: BEGIN %d\n", rank, i);
    // generate unique fname
    sprintf(fname, "%d_%.*s_%d_%d", meta.uid, (int)strlen(meta.tid) - 1, meta.tid, rank, i);
    pid = exec_script(pfd, fname, meta.type); 
    
    // echo output of script
    while (!DORMANT && !SHUTDOWN && (nbytes = read(pfd[0], buff, MAX_BUFF)) > 0) {
      buff[nbytes] = '\0';
      printf("P%d: SUBPROC: %s", rank, buff);
    } 

    close(pfd[0]);

    // check if EOF or SIGUSR
    if (DORMANT) {
      kill(pid, SIGINT);
      waitpid(pid, NULL, 0);
      pause();
    } else if (SHUTDOWN){
      printf("P%d: ATEMPTING SHUTDOWN\n", rank);
      kill(pid, SIGINT);
      waitpid(pid, NULL, 0);
    } else {
      waitpid(pid, NULL, 0);
      printf("P%d: COMPLETED %s\n", rank, fname);
    }
  }
  printf("P%d: FINISHED\n", rank);
  fflush(stdout);
  exit(0);
} 

pid_t exec_script(int *pfd, char *fname, char *type) {
  pid_t pid;

  printf("%s\n", type);
  fflush(stdout);
 
 if (pipe(pfd) == -1)
    die("pipe");
  if ((pid=fork()) == -1)
    die("fork");
  if (pid == 0) {
    signal(SIGUSR1, SIG_DFL);
    signal(SIGUSR2, SIG_DFL);
    dup2(pfd[1], STDOUT_FILENO);
    close(pfd[0]); 
    close(pfd[1]);
    if (strcmp(type, "SSS") == 0)
      execl("/var/www/fastGIS/venv/bin/python", 
	    "python",  "/var/www/fastGIS/app/scripts/sss.py", 
	    fname, (char*)0 );
    else
      execl("/var/www/fastGIS/venv/bin/python", 
	    "python",  "/var/www/fastGIS/app/scripts/sgs.py", 
	    fname, (char*)0 );
    die("execl");
  }
  close(pfd[1]);
  return pid;
}


int do_master(int comm_size) {
  char buff[MAX_BUFF];
  char *cptr;
  int i=0;
  
  while (1) {
    fgets(buff, MAX_BUFF, stdin);
    if ( (cptr = strchr(buff, '\n')) != NULL) *cptr = '\0';
    
    if (strcmp(buff, "SHUTDOWN") == 0) {
      printf("Master init shutdown\n");	
      send_all(comm_size, buff);
      break;
    } 
    else if (strcmp(buff, "PAUSE") == 0) {
      printf("Master init pause\n");
      send_all(comm_size, buff);
    }
    else if (strcmp(buff, "FINISHED") == 0) {
      printf("Master: FINISHED\n");
      send_all(comm_size, buff);
      break;
    }
    else 
      send_all(comm_size, buff);
    fflush(stdout);  
  } // end while
}

int send_all(int comm_size, char* msg) {
  int i = 0;
  while (++i < comm_size) 
    MPI_Send(msg, strlen(msg) + 1, MPI_CHAR, i, 0, MPI_COMM_WORLD);
}
