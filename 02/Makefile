CFLAGS ?= -Wall -Wextra -O2

all: alice_bob

alice_bob: alice_bob.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	rm -f alice_bob
