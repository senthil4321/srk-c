/*
 * alice_bob.c - A to B and B to A: how Alice and Bob talk securely
 *
 * In cryptography the two parties are called Alice (A) and Bob (B).
 * This program walks through the classic flow step by step:
 *
 *   1. Key exchange (Diffie-Hellman)
 *        A -> B : A's public value
 *        B -> A : B's public value
 *      Both sides now compute the same shared secret,
 *      but the secret itself is never sent.
 *
 *   2. Secure messages, using a key derived from that secret
 *        A -> B : encrypted message + tag
 *        B -> A : encrypted reply   + tag
 *
 *   3. An attacker (Eve) changes a message in transit, and the
 *      receiver detects it.
 *
 * WARNING: for learning only. The numbers are tiny and the cipher
 * and tag are toys. Real systems use X25519 or ECDH, AES-GCM or
 * ChaCha20-Poly1305, and HKDF.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* Public parameters both sides agree on: a prime p and a generator g.
 * p < 2^32, so a * b fits in 64 bits during modular multiplication. */
#define P 4294967291ULL /* largest prime below 2^32 */
#define G 5ULL

#define MAX_MSG 128

/* (base ^ exp) mod m, using square-and-multiply */
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t m)
{
    uint64_t result = 1;

    base %= m;
    while (exp > 0) {
        if (exp & 1)
            result = (result * base) % m;
        base = (base * base) % m;
        exp >>= 1;
    }
    return result;
}

/* Tiny pseudo-random generator (xorshift64), used as a keystream */
static uint64_t xorshift64(uint64_t *state)
{
    uint64_t x = *state;

    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

/* Turn the shared secret into a key for one direction.
 * A->B and B->A get different keys, so a message from one
 * direction can't be replayed in the other. */
static uint64_t derive_key(uint64_t shared, char direction)
{
    uint64_t k = shared * 0x9E3779B97F4A7C15ULL ^ (uint64_t)direction;

    return k ? k : 1; /* xorshift state must not be 0 */
}

/* Encrypt or decrypt: XOR with the keystream (the same operation both ways) */
static void xor_cipher(uint8_t *buf, size_t len, uint64_t key)
{
    uint64_t state = key;
    size_t i;

    for (i = 0; i < len; i++)
        buf[i] ^= (uint8_t)xorshift64(&state);
}

/* Toy message tag (FNV-1a over key + data), stands in for an HMAC */
static uint64_t make_tag(const uint8_t *buf, size_t len, uint64_t key)
{
    uint64_t h = 1469598103934665603ULL;
    size_t i;

    for (i = 0; i < 8; i++) {
        h ^= (uint8_t)(key >> (i * 8));
        h *= 1099511628211ULL;
    }
    for (i = 0; i < len; i++) {
        h ^= buf[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static void print_hex(const char *label, const uint8_t *buf, size_t len)
{
    size_t i;

    printf("    %-11s ", label);
    for (i = 0; i < len; i++)
        printf("%02x", buf[i]);
    printf("\n");
}

/* Send a message from one side to the other: encrypt, tag, and
 * (optionally) let Eve change one byte before it is delivered. */
static void send_message(const char *from, const char *to, char dir,
                         uint64_t sender_secret, uint64_t receiver_secret,
                         const char *text, int tamper)
{
    uint8_t wire[MAX_MSG];
    size_t len = strlen(text);
    uint64_t send_key = derive_key(sender_secret, dir);
    uint64_t recv_key = derive_key(receiver_secret, dir);
    uint64_t tag;

    if (len >= MAX_MSG)
        len = MAX_MSG - 1;

    printf("\n  %s -> %s : \"%s\"\n", from, to, text);

    /* Sender side */
    memcpy(wire, text, len);
    xor_cipher(wire, len, send_key);
    tag = make_tag(wire, len, send_key);
    print_hex("ciphertext:", wire, len);
    printf("    tag:        %016llx\n", (unsigned long long)tag);

    /* On the network */
    if (tamper) {
        wire[0] ^= 0x01;
        printf("    !! Eve flips one bit of the ciphertext in transit\n");
    }

    /* Receiver side: check the tag first, then decrypt */
    if (make_tag(wire, len, recv_key) != tag) {
        printf("    %s: tag mismatch -> message REJECTED\n", to);
        return;
    }
    xor_cipher(wire, len, recv_key);
    wire[len] = '\0';
    printf("    %s: tag OK, decrypted: \"%s\"\n", to, (char *)wire);
}

int main(void)
{
    /* Private keys: chosen at random in real life, never shared */
    uint64_t a_private = 123456789ULL;
    uint64_t b_private = 987654321ULL;
    uint64_t a_public, b_public;
    uint64_t a_shared, b_shared;

    printf("=== Public parameters ===\n");
    printf("  p = %llu, g = %llu\n",
           (unsigned long long)P, (unsigned long long)G);

    printf("\n=== Step 1: Key exchange (Diffie-Hellman) ===\n");
    a_public = mod_pow(G, a_private, P);
    b_public = mod_pow(G, b_private, P);

    printf("  A -> B : A's public value  g^a mod p = %llu\n",
           (unsigned long long)a_public);
    printf("  B -> A : B's public value  g^b mod p = %llu\n",
           (unsigned long long)b_public);

    a_shared = mod_pow(b_public, a_private, P); /* (g^b)^a */
    b_shared = mod_pow(a_public, b_private, P); /* (g^a)^b */

    printf("  A computes (g^b)^a mod p = %llu\n", (unsigned long long)a_shared);
    printf("  B computes (g^a)^b mod p = %llu\n", (unsigned long long)b_shared);
    printf("  Shared secrets %s\n",
           a_shared == b_shared ? "MATCH" : "DO NOT MATCH");
    printf("  Eve only saw the public values, not a, b, or the secret.\n");

    printf("\n=== Step 2: Secure messages ===");
    send_message("A", "B", 'A', a_shared, b_shared, "Hi Bob, it's Alice!", 0);
    send_message("B", "A", 'B', b_shared, a_shared, "Hello Alice, got it.", 0);

    printf("\n=== Step 3: Tampering is detected ===");
    send_message("A", "B", 'A', a_shared, b_shared, "Pay Eve $0", 1);

    return 0;
}
