#include <stdio.h>
#include <stdlib.h>

int main(void) {
    FILE *fp = fopen("/flag.txt", "r");
    if (!fp) {
        perror("Error opening /flag.txt");
        return EXIT_FAILURE;
    }

    char buffer[1024];
    size_t n;
    while ((n = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        fwrite(buffer, 1, n, stdout);
    }

    fclose(fp);
    return EXIT_SUCCESS;
}
