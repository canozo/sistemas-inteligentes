#include <string.h>
#include <stdlib.h>
#include "bucket.h"

bucket_t *new_bucket(char *command, int cmd_len) {
  bucket_t *this = (bucket_t *) malloc(sizeof(*this));

  memcpy(this->searching, command, cmd_len);
  this->searching[cmd_len] = 0;

  this->meant[0] = 0;
  this->found = 0;

  return this;
}
