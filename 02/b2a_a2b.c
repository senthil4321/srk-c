/*
 * b2a_a2b.c - Goubin's conversion between Boolean and arithmetic masking
 *
 * Reference: L. Goubin, "A Sound Method for Switching between Boolean
 * and Arithmetic Masking", CHES 2001.
 *
 * Side-channel masking: to stop power/EM analysis from seeing a secret
 * x, we never handle x directly. We split it into two shares, using a
 * random mask r:
 *
 *   Boolean masking:    x = x' ^ r          (good for XOR, AND, S-boxes)
 *   Arithmetic masking: x = A + r mod 2^32  (good for +, -)
 *
 * Ciphers that mix XOR and + (ChaCha, SHA-2, ARX designs) need to
 * switch between the two forms without ever computing x itself:
 *
 *   B2A: (x', r) -> A   with A + r == x' ^ r
 *   A2B: (A, r)  -> x'  with x' ^ r == A + r
 *
 * Note: this is a teaching demo. The C compiler may reorder or merge
 * these operations, so real protected code also needs a check of the
 * generated assembly (or is written in assembly), and a proper random
 * number generator.
 */
#include <stdio.h>
#include <stdint.h>
#include <time.h>

#define K 32 /* word size in bits */

/* Small PRNG (xorshift32) for masks. Not cryptographically secure. */
static uint32_t rng_state = 2463534242u;

static uint32_t rand32(void)
{
    uint32_t x = rng_state;

    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

/* ---- Naive conversions: correct, but they LEAK x ---- */

static uint32_t b2a_naive(uint32_t xp, uint32_t r)
{
    uint32_t x = xp ^ r; /* x is now in a register: leak */

    return x - r;
}

static uint32_t a2b_naive(uint32_t A, uint32_t r)
{
    uint32_t x = A + r; /* x is now in a register: leak */

    return x ^ r;
}

/* ---- Goubin's Boolean to arithmetic ----
 *
 * For fixed x', the function Phi(r) = (x' ^ r) - r is affine over
 * GF(2), so Phi(r) = Phi(g) ^ Phi(g ^ r) ^ Phi(0), and Phi(0) = x'.
 * Using a fresh random g, every intermediate is masked by g or r.
 */
static uint32_t b2a_goubin(uint32_t xp, uint32_t r)
{
    uint32_t g = rand32();
    uint32_t T, A;

    T = xp ^ g;     /* x' ^ g          */
    T = T - g;      /* Phi(g)          */
    T = T ^ xp;     /* Phi(g) ^ Phi(0) */
    g = g ^ r;      /* g ^ r           */
    A = xp ^ g;     /* x' ^ g ^ r      */
    A = A - g;      /* Phi(g ^ r)      */
    A = A ^ T;      /* A = x - r       */
    return A;
}

/* ---- Goubin's arithmetic to Boolean ----
 *
 * Addition is not linear over XOR because of carries, so the carry
 * chain is rebuilt bit by bit (K-1 rounds) under a random mask g.
 */
static uint32_t a2b_goubin(uint32_t A, uint32_t r)
{
    uint32_t g = rand32();
    uint32_t T, xp, O;
    int i;

    T = g << 1;
    xp = g ^ r;
    O = g & xp;
    xp = T ^ A;
    g = g ^ xp;
    g = g & r;
    O = O ^ g;
    g = T & A;
    O = O ^ g;
    for (i = 1; i < K; i++) {
        g = T & r;
        g = g ^ O;
        T = T & A;
        g = g ^ T;
        T = g << 1;
    }
    xp = xp ^ T;
    return xp;
}

/* Run many random conversions and edge cases; return the number of failures */
static unsigned long self_test(unsigned long n)
{
    static const uint32_t edge[] = { 0, 1, 0x7FFFFFFFu, 0x80000000u, 0xFFFFFFFFu };
    unsigned long fails = 0, i;
    size_t a, b;

    for (a = 0; a < 5; a++) {
        for (b = 0; b < 5; b++) {
            uint32_t x = edge[a], r = edge[b];

            if (b2a_goubin(x ^ r, r) + r != x)
                fails++;
            if ((a2b_goubin(x - r, r) ^ r) != x)
                fails++;
        }
    }
    for (i = 0; i < n; i++) {
        uint32_t x = rand32(), r = rand32();

        if (b2a_goubin(x ^ r, r) + r != x)
            fails++;
        if ((a2b_goubin(x - r, r) ^ r) != x)
            fails++;
    }
    return fails;
}

int main(void)
{
    uint32_t x = 0xCAFEBABEu; /* the secret */
    uint32_t r, xp, A, xp2;
    unsigned long n = 1000000, fails;

    rng_state ^= (uint32_t)time(NULL);
    if (rng_state == 0)
        rng_state = 1;
    r = rand32();

    printf("=== Secret and masks ===\n");
    printf("  secret x            = 0x%08X\n", (unsigned)x);
    printf("  random mask r       = 0x%08X\n", (unsigned)r);
    xp = x ^ r;
    printf("  Boolean share  x'   = x ^ r = 0x%08X\n", (unsigned)xp);

    printf("\n=== Naive conversion (leaks x) ===\n");
    printf("  B2A: (x' ^ r) - r   -> computes x' ^ r = 0x%08X == x !\n",
           (unsigned)(xp ^ r));
    A = b2a_naive(xp, r);
    printf("       A = 0x%08X\n", (unsigned)A);
    printf("  A2B: (A + r) ^ r    -> computes A + r  = 0x%08X == x !\n",
           (unsigned)(A + r));
    printf("       x' = 0x%08X\n", (unsigned)a2b_naive(A, r));

    printf("\n=== Goubin B2A: Boolean -> arithmetic ===\n");
    A = b2a_goubin(xp, r);
    printf("  input  x' = 0x%08X, r = 0x%08X\n", (unsigned)xp, (unsigned)r);
    printf("  output A  = 0x%08X\n", (unsigned)A);
    printf("  check  A + r = 0x%08X  %s\n", (unsigned)(A + r),
           A + r == x ? "== x  OK" : "!= x  FAIL");

    printf("\n=== Goubin A2B: arithmetic -> Boolean ===\n");
    xp2 = a2b_goubin(A, r);
    printf("  input  A  = 0x%08X, r = 0x%08X\n", (unsigned)A, (unsigned)r);
    printf("  output x' = 0x%08X\n", (unsigned)xp2);
    printf("  check  x' ^ r = 0x%08X  %s\n", (unsigned)(xp2 ^ r),
           (xp2 ^ r) == x ? "== x  OK" : "!= x  FAIL");
    printf("  round trip: x' %s the original Boolean share\n",
           xp2 == xp ? "matches" : "DOES NOT match");

    printf("\n=== Self-test: %lu random cases + edge cases ===\n", n);
    fails = self_test(n);
    printf("  %s (%lu failures)\n", fails ? "FAIL" : "PASS", fails);

    return fails ? 1 : 0;
}
