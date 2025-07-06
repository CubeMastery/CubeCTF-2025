#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

const char fmt[] = "                  ,d88b.d88b,  \n"
                   "                  88888888888  \n"
                   "                  'Y8888888Y   \n"
                   "                    'Y888Y'    \n"
                   "                      'Y'      \n"
                                         "%*s      \n"
                   "                will u be mine?\n\n";

char* valentine;
int name_len, valentine_len;

int main() {
  setbuf(stdin, NULL);  // ignore
  setbuf(stdout, NULL); // ignore

  char name[24];          // sadly, you and your valentine
  valentine = malloc(24); // are eternally separated by
                          // unmapped memory

  printf("who is your valentine? ");
  scanf("%23[^\n]%*c", valentine);    // examples: "katniss", "nick wilde"
  printf("what is your name? ");
  scanf("%23[^\n]%*c", name);         // examples: "steve", "alex"

  name_len = strlen(name);
  valentine_len = strlen(valentine);

  if (name_len > 23 || valentine_len > 23) { // super secret proprietary algorithm
    printf("unfortunately, %1s and %1s are not compatible.\n", name, valentine);
    _exit(-1);
  }

  printf(name); // bridge the gap between you and your valentine
  printf(", here is your card for %1s:\n\n", valentine);
  printf(fmt, 24+valentine_len/2, valentine); // this isn't vulnerable i promise

  return 0;
}
