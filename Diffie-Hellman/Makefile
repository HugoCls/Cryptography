CC=gcc
CFLAGS=-Wno-deprecated-declarations
LDLIBS=-lcrypto

all: alice bob

alice: alice.c
	$(CC) $(CFLAGS) -o alice alice.c $(LDLIBS)

bob: bob.c
	$(CC) $(CFLAGS) -o bob bob.c $(LDLIBS)

clean:
	rm -f alice bob
