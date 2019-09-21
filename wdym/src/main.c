#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <sqlite3.h>
#include "bucket.h"

typedef struct meaning_t {
  char said[15];
  char meant[15];
} meaning_t;

char **split(char *);
int supported(char *);
void execute(char **);
bucket_t *search(sqlite3 *, char *);
int cb_check_exists(void *, int, char **, char **);
void did_you_mean(sqlite3 *, char *);
void guardarDB(sqlite3 *, char *, int, char *);
void switch_chars(char *, int);

const int supp_size = 5;
const char *supp_commands[] = {
  "ls",
  "ld",
  "ping",
  "cat",
  "top"
};

const char *teclado[] = {
  "qwertyuiop",
  "asdfghjkl ",
  "zxcvbnm   "
};

int main(int argc, char *argv[]) {
  if (argc < 2) {
    fprintf(stderr, "parametros: ./<ejecutable> <base de datos sqlite>\n");
    fprintf(stderr, "parametros: ./main.exe ../wdym.db\n");
    return 1;
  }

  size_t bufsize = 128;
  size_t read;
  char *buffer = (char *) malloc(bufsize);

  sqlite3 *db;
  if (sqlite3_open(argv[1], &db)) {
    fprintf(stderr, "Error al abrir db: %s\n", sqlite3_errmsg(db));
    return 1;
  }

  while (1) {
    printf("> ");
    read = getline(&buffer, &bufsize, stdin);
    buffer[read - 1] = 0;

    if (strcmp(buffer, "exit") == 0) {
      break;
    }

    char **vector = split(buffer);

    if (!supported(vector[0])) {
      bucket_t *bucket = search(db, vector[0]);
      if (bucket->found) {
        // se encontro la correccion en la db
        printf("Supongo que quiso decir \"%s\" en lugar de \"%s\"!\n", bucket->meant, vector[0]);
        int meant_len = strlen(bucket->meant);
        memcpy(vector[0], bucket->meant, meant_len);
        vector[meant_len] = 0;
      } else {
        did_you_mean(db, vector[0]);
      }

      free(bucket);
    }

    // exec
    execute(vector);
  }

  sqlite3_close(db);
  free(buffer);
  return 0;
}

char **split(char *input) {
  // tomar una cadena y hacerle un split por cada espacio:
  // "ls -l" => ["ls", "-l"]

  int allocated = 4;
  char **res = (char **) malloc(sizeof(*res) * allocated);

  int size = 0;
  char *token = strtok(input, " \t");
  while (token != NULL) {
    if (size >= allocated) {
      allocated *= 2;
      res = realloc(res, sizeof(*res) * allocated);
    }

    res[size] = token;
    size += 1;
    token = strtok(NULL, " \t");
  }

  if (allocated > size) {
    res[size] = 0;
  }

  return res;
}

int supported(char *command) {
  // revisar si el comando que envio esta en la lista
  for (int i = 0; i < supp_size; i += 1) {
    if (strcmp(command, supp_commands[i]) == 0) {
      return 1;
    }
  }
  return 0;
}

void execute(char **vector) {
  int child = fork();
  if (child == 0) {
    execvp(vector[0], vector);

    // si llega a este punto hubo un error
    fprintf(stderr, "error: comando \"%s\" no se pudo ejecutar.\n", vector[0]);
    exit(1);
  } else {
    wait(&child);
    free(vector);
  }
}

bucket_t *search(sqlite3 *db, char *command) {
  int len_cmd = strlen(command);
  bucket_t *bucket = new_bucket(command, len_cmd);

  char *error;
  int code = sqlite3_exec(db, "select * from meanings", cb_check_exists, bucket, &error);
  if (code != SQLITE_OK) {
    fprintf(stderr, "Error SQL: %s\n", error);
    sqlite3_free(error);
  }

  return bucket;
}

int cb_check_exists(void *passed, int count, char **data, char **columns) {
  // revisar la db, viendo si ya se ha hecho una correccion con el comando
  meaning_t meaning;
  for(int i = 0; i < count; i += 1) {
    int len = strlen(data[i]);
    if (strcmp(columns[i], "said") == 0) {
      memcpy(meaning.said, data[i], len);
      meaning.said[len] = 0;
    } else {
      memcpy(meaning.meant, data[i], len);
      meaning.meant[len] = 0;
    }
  }

  bucket_t *bucket = (bucket_t *) passed;
  if (strcmp(bucket->searching, meaning.said) == 0) {
    // se ha hecho una correccion anteriormente
    bucket->found = 1;
    int meant_len = strlen(meaning.meant);
    memcpy(bucket->meant, meaning.meant, meant_len);
    bucket->meant[meant_len] = 0;
  }

  return 0;
}

void did_you_mean(sqlite3 *db, char *command) {
  char meant[15];
  int similarity = 0;
  int switched = 0;
  int diff_pos;

  int len_cmd = strlen(command);

  for (int i = 0; i < supp_size; i += 1) {
    // mismo tamanio
    if (len_cmd == strlen(supp_commands[i])) {
      // mismos caracteres excepto uno
      int diferentes = 0;

      for (int j = 0; j < len_cmd; j += 1) {
        if (command[j] != supp_commands[i][j]) {
          diferentes += 1;
          diff_pos = j;
        }
      }

      if (diferentes == 1) {
        // es posible que typeo mal el comando
        memcpy(meant, supp_commands[i], len_cmd);
        meant[len_cmd] = 0;
        similarity = 1;
        break;
      }

      // switch dos caracteres consecutivos a ver si son iguales al comando con el typo
      for (int j = 0; j < len_cmd - 1; j += 1) {
        switch_chars(command, j);
        if (strcmp(command, supp_commands[i]) == 0) {
          // typeo mal el comando
          memcpy(meant, supp_commands[i], len_cmd);
          meant[len_cmd] = 0;
          switched = 1;
        }
        switch_chars(command, j);
        if (switched) break;
      }
      if (switched) break;
    }
  }

  if (switched) {
    guardarDB(db, command, len_cmd, meant);
  } else if (similarity) {
    // revisar en el teclado si typeo mal
    char typo = tolower(command[diff_pos]);
    char correcto = tolower(meant[diff_pos]);

    // buscar la tecla correcta en el teclado y ver si el typo esta alrededor
    int found = 0;
    int fila, columna;
    for (int i = 0; i < 3; i += 1) {
      if (found) break;
      for (int j = 0; j < 10; j += 1) {
        if (tolower(teclado[i][j]) == correcto && !found) {
          fila = i;
          columna = j;
          found = 1;
          break;
        }
      }
    }

    // revisar si la tecla del typo se encuentra alrededor (en el teclado) de la correcta
    int f = 0, tfila, tcolumna;
    for (int i = -1; i <= 1; i += 1) {
      tfila = fila + i >= 0 && fila + i <= 2 ? fila + i : fila;
      for (int j = -1; j <= 1; j += 1) {
        if (i == 0 && j == 0) continue;
        tcolumna = columna + j >= 0 && columna + j <= 9 ? columna + j : columna;
        f = f || tolower(teclado[tfila][tcolumna]) == typo;
      }
    }

    if (f) {
      guardarDB(db, command, len_cmd, meant);
    }
  }
}

void guardarDB(sqlite3 *db, char *command, int len_cmd, char *meant) {
  // preguntar si quiere guardar en la db
  size_t bufsize = 15;
  size_t read;
  char *buffer = (char *) malloc(bufsize);
  buffer[0] = 0;

  printf("Quiso decir \"%s\" en lugar de \"%s\"? [y/N] ", meant, command);
  read = getline(&buffer, &bufsize, stdin);
  buffer[read - 1] = 0;

  if (strcmp(buffer, "y") == 0) {
    char *error;
    size_t needed = snprintf(NULL, 0, "insert into meanings values ('%s', '%s')", command, meant);
    char *sql = (char *) malloc(needed + 1);
    sprintf(sql, "insert into meanings values ('%s', '%s')", command, meant);

    int code = sqlite3_exec(db, sql, 0, 0, &error);
    if (code != SQLITE_OK) {
      fprintf(stderr, "Error SQL: %s\n", error);
      sqlite3_free(error);
    } else {
      printf("Se guardo la correccion!\n");
      memcpy(command, meant, len_cmd);
      command[len_cmd] = 0;
    }

    free(sql);
  }

  free(buffer);
}

void switch_chars(char *string, int pos) {
  char temp = string[pos + 1];
  string[pos + 1] = string[pos];
  string[pos] = temp;
}
