#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <flag>\n", argv[0]);
    return 1;
  }
  const char *flag = argv[1];
  char mask[] = {' ', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4',
                 '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
                 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '{', '}'};
  size_t flag_len = strlen(flag);
  size_t mask_len = sizeof(mask) / sizeof(mask[0]);

  srand(time(NULL));

  while (1) {
    putchar('\r');
    for (size_t i = 0; i < flag_len; ++i) {
      mask[0] = flag[i];
      putchar(mask[rand() % mask_len]);
    }
    fflush(stdout);
    usleep(10000);
  }

  return 0;
}
