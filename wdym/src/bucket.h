#ifndef BUCKET_H
#define BUCKET_H

typedef struct bucket_t {
  char searching[15];
  int found;
  char meant[15];
} bucket_t;

bucket_t *new_bucket(char *, int);

#endif
