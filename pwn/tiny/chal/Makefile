CC = c99
CFLAGS = -Wall -O2 -fcf-protection=none -D_FORTIFY_SOURCE=0 -fno-stack-protector

# LIB = -lpthread

all: tiny

tiny: tiny.c
	$(CC) $(CFLAGS) -o tiny tiny.c $(LIB)

clean:
	rm -f *.o tiny *~
