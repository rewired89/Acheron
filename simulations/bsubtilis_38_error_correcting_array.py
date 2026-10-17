"""
Acheron Simulation 38: One Bit per Cell, Many Cells, and an Error-Correcting
Code: How Long Does a Word Last?
=====================================================================

PURPOSE:
bsubtilis_37 found that putting several toggles in ONE cell fails through
leakage between them. The other way to store a word is one bit per cell (or per
spot) across many cells, so there is no leakage, and to add redundancy so a few
wrong bits do not ruin the word. This file asks how many cells that costs and
how long the word lasts, as a function of the per-bit flip rate.

INPUT FROM EARLIER WORK:
bsubtilis_35 measured first-flip rates of the molecular toggle between about
0.0001 and 0.011 per hour depending on molecules per cell and burst size (a
simulation result at assumed molecule counts, not a measurement). Here the
per-bit flip rate lambda is a SWEEP AXIS spanning that range. Each bit is a
symmetric two-state switch: each state flips to the other at rate lambda, so
P(bit wrong at time t) = 0.5 (1 - exp(-2 lambda t)), which saturates at 0.5.

SCHEMES (K data bits, here 32 = 4 bytes):
none; repetition x3 and x5 (majority vote per data bit); Hamming(7,4),
Hamming(15,11) and Hamming(31,26) (each block corrects one wrong bit).
Cost = cells per word. Success = the decoder returns all K data bits right.
These are exact formulas (checked against a Monte Carlo that runs real encoders
and decoders). When 32 is not a multiple of the code's data length the last block is
padded and the formula requires the padding to decode right too, which is slightly
pessimistic for Hamming(15,11) and Hamming(31,26).

COMMON-CAUSE FAILURE (the weakness of any code):
Shocks hit the whole array at rate h per hour (a contamination, a medium change,
loss of the circuit, a sporulation wave); each shock flips each cell's bit
independently with probability f. Many errors at once defeat a code that
corrects only a few. Given N shocks the bits are independent with
1 - 2 p = exp(-2 lambda t) (1 - 2 f)^N, and N is Poisson(h t); the word
success is averaged over N.

WHAT THIS DOES NOT DO:
Flip rate, shock rate h and shock size f are sweep axes, not measurements. Bit
errors are otherwise independent. No readout error (a misread cell would add
errors on top), no cell loss or erasure, no addressing of spots, no rewriting or
refreshing (periodic re-reading and rewriting would extend life a lot and is not
modelled), and no cost of the reading hardware. Hamming codes are the simplest
choice, not the best one.
"""

import math
import random
from math import comb

import numpy as np

K_DATA = 32
HOURS = {'1 day': 24.0, '1 week': 168.0, '1 month': 720.0}


# ------------------------------------------------------------------- codes
def hamming_params(m):
    n = 2 ** m - 1
    return n, n - m


def hamming_encode(data, m):
    n, k = hamming_params(m)
    assert len(data) == k
    code = [0] * (n + 1)
    di = 0
    for pos in range(1, n + 1):
        if pos & (pos - 1):
            code[pos] = data[di]
            di += 1
    for i in range(m):
        p = 1 << i
        code[p] = sum(code[pos] for pos in range(1, n + 1) if pos & p and pos != p) % 2
    return code[1:]


def hamming_decode(word, m):
    n, k = hamming_params(m)
    code = [0] + list(word)
    syn = 0
    for i in range(m):
        p = 1 << i
        if sum(code[pos] for pos in range(1, n + 1) if pos & p) % 2:
            syn |= p
    if 1 <= syn <= n:
        code[syn] ^= 1
    return [code[pos] for pos in range(1, n + 1) if pos & (pos - 1)]


def rep_encode(data, r):
    return [b for b in data for _ in range(r)]


def rep_decode(word, r):
    return [1 if sum(word[i * r:(i + 1) * r]) * 2 > r else 0 for i in range(len(word) // r)]


SCHEMES = [
    ('no code', 'none', None),
    ('repeat x3', 'rep', 3),
    ('repeat x5', 'rep', 5),
    ('Hamming(7,4)', 'ham', 3),
    ('Hamming(15,11)', 'ham', 4),
    ('Hamming(31,26)', 'ham', 5),
]


def cells_for(kind, par):
    if kind == 'none':
        return K_DATA
    if kind == 'rep':
        return K_DATA * par
    n, k = hamming_params(par)
    return math.ceil(K_DATA / k) * n


def success_given_p(kind, par, p):
    """Exact probability that all K_DATA data bits decode right when each stored
    bit is independently wrong with probability p."""
    if kind == 'none':
        return (1 - p) ** K_DATA
    if kind == 'rep':
        r = par
        ok = sum(comb(r, j) * p ** j * (1 - p) ** (r - j) for j in range(0, (r - 1) // 2 + 1))
        return ok ** K_DATA
    n, k = hamming_params(par)
    block_ok = (1 - p) ** n + n * p * (1 - p) ** (n - 1)
    return block_ok ** math.ceil(K_DATA / k)


def p_wrong(lam, t, h=0.0, f=0.0, N=0):
    return 0.5 * (1.0 - math.exp(-2.0 * lam * t) * (1.0 - 2.0 * f) ** N)


def word_success(kind, par, lam, t, h=0.0, f=0.0):
    if h <= 0 or f <= 0:
        return success_given_p(kind, par, p_wrong(lam, t))
    mean = h * t
    top = int(mean + 12 * math.sqrt(mean + 1) + 5)
    total = 0.0
    for N in range(top + 1):
        w = math.exp(-mean + N * math.log(mean) - math.lgamma(N + 1)) if mean > 0 else float(N == 0)
        total += w * success_given_p(kind, par, p_wrong(lam, t, h, f, N))
    return total


def time_to(kind, par, lam, level, h=0.0, f=0.0, t_max=1e5):
    if word_success(kind, par, lam, 1e-9, h, f) < level:
        return 0.0
    if word_success(kind, par, lam, t_max, h, f) >= level:
        return float('inf')
    lo, hi = 1e-9, t_max
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if word_success(kind, par, lam, mid, h, f) >= level:
            lo = mid
        else:
            hi = mid
    return lo


# ------------------------------------------------------------------- checks
def self_check(n_mc=4000, seed=7):
    rnd = random.Random(seed)
    for m in (3, 4, 5):
        n, k = hamming_params(m)
        for _ in range(200):
            d = [rnd.randint(0, 1) for _ in range(k)]
            c = hamming_encode(d, m)
            assert hamming_decode(c, m) == d
            c2 = list(c)
            c2[rnd.randrange(n)] ^= 1
            assert hamming_decode(c2, m) == d, "Hamming failed to fix a single error"
    for r in (3, 5):
        d = [rnd.randint(0, 1) for _ in range(40)]
        c = rep_encode(d, r)
        c2 = list(c)
        for i in range(0, len(c2), r):
            c2[i] ^= 1
        assert rep_decode(c2, r) == d
    rows = []
    for (name, kind, par) in SCHEMES[1:]:
        p = 0.02
        ok = 0
        for _ in range(n_mc):
            d = [rnd.randint(0, 1) for _ in range(K_DATA)]
            if kind == 'rep':
                c = rep_encode(d, par)
            else:
                n, k = hamming_params(par)
                pad = d + [0] * (math.ceil(K_DATA / k) * k - K_DATA)
                c = [b for i in range(0, len(pad), k) for b in hamming_encode(pad[i:i + k], par)]
            c = [b ^ (1 if rnd.random() < p else 0) for b in c]
            if kind == 'rep':
                dec = rep_decode(c, par)
            else:
                n, k = hamming_params(par)
                dec = [b for i in range(0, len(c), n) for b in hamming_decode(c[i:i + n], par)]
                d = pad  # the formula requires every block, padding included, to decode right
            ok += int(dec == d)
        rows.append((name, ok / n_mc, success_given_p(kind, par, p)))
    return rows


# ------------------------------------------------------------------- report
def fmt_t(t):
    if t == float('inf'):
        return '>10^5 h'
    if t < 1:
        return f'{t * 60:.0f} min'
    if t < 48:
        return f'{t:.0f} h'
    return f'{t / 24:.0f} d'


def main():
    print("=" * 92)
    print("0) CODE SELF-CHECK: real encoders and decoders against the exact formula (per-bit error 2%)")
    print("=" * 92)
    for name, mc, ex in self_check():
        print(f"  {name:<16} Monte Carlo {mc:>6.1%}   formula {ex:>6.1%}")
    print("  (all single-error cases decode right; repetition survives one wrong copy per bit)")

    print("\n" + "=" * 92)
    print(f"1) COST: cells needed to store {K_DATA} data bits ({K_DATA // 8} bytes)")
    print("=" * 92)
    for name, kind, par in SCHEMES:
        c = cells_for(kind, par)
        print(f"  {name:<16}{c:>6} cells   ({c / K_DATA:.2f} cells per data bit)")

    lams = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
    print("\n" + "=" * 92)
    print("2) HOW LONG UNTIL THE WORD HAS A 50% / 90% CHANCE OF BEING INTACT (no shocks, no refresh)")
    print("   per-bit flip rate lambda per hour; each entry is time to 50% | time to 90%")
    print("=" * 92)
    print(f"{'lambda':>8}" + "".join(f"{s[0]:>20}" for s in SCHEMES))
    for lam in lams:
        row = f"{lam:>8g}"
        for (name, kind, par) in SCHEMES:
            row += f"{fmt_t(time_to(kind, par, lam, 0.5)) + ' | ' + fmt_t(time_to(kind, par, lam, 0.9)):>20}"
        print(row)

    print("\n" + "=" * 92)
    print("3) WORD SUCCESS AT 1 DAY / 1 WEEK / 1 MONTH, by flip rate (no shocks)")
    print("=" * 92)
    for lam in (3e-4, 1e-3, 3e-3):
        print(f"\nlambda = {lam:g} per hour")
        print(f"{'':<16}" + "".join(f"{k:>12}" for k in HOURS))
        for (name, kind, par) in SCHEMES:
            print(f"{name:<16}" + "".join(f"{word_success(kind, par, lam, t):>12.1%}" for t in HOURS.values()))

    print("\n" + "=" * 92)
    print("4) COMMON-CAUSE SHOCKS, lambda = 0.0003 per hour, word success after 1 week")
    print("   h = shocks per hour, f = fraction of cells flipped by one shock")
    print("=" * 92)
    t = HOURS['1 week']
    conds = [(0.0, 0.0), (1e-3, 0.05), (1e-3, 0.3), (1e-2, 0.05), (1e-2, 0.3)]
    print(f"{'':<16}" + "".join(f"{('none' if h == 0 else f'h={h:g},f={f:g}'):>16}" for h, f in conds))
    for (name, kind, par) in SCHEMES:
        print(f"{name:<16}" + "".join(f"{word_success(kind, par, 3e-4, t, h, f):>16.1%}" for h, f in conds))
    print("\nA shock that flips a large fraction of cells at once defeats every code here; redundancy only helps")
    print("against independent flips.")

    print("\n" + "=" * 92)
    print("5) REFRESH: read, decode and rewrite the whole word every tau hours (assumed to be done perfectly)")
    print("   word success after 1 month, lambda = 0.001 per hour, no shocks")
    print("   success = (success within one interval) ** (intervals); a failed decode is permanent")
    print("=" * 92)
    taus = [None, 24.0, 6.0, 2.0]
    print(f"{'':<16}" + "".join(f"{('no refresh' if t is None else f'every {t:g} h'):>14}" for t in taus))
    T = HOURS['1 month']
    for (name, kind, par) in SCHEMES[1:]:
        row = f"{name:<16}"
        for tau in taus:
            if tau is None:
                v = word_success(kind, par, 1e-3, T)
            else:
                v = word_success(kind, par, 1e-3, tau) ** (T / tau)
            row += f"{v:>14.1%}"
        print(row)
    print("\nRefresh needs a reader and a writer for every cell and assumes the rewrite itself adds no error, so")
    print("it is an upper bound. It turns a short retention time into a long one at the price of hardware and an")
    print("upper limit set by the reader and writer, not by the cells.")


if __name__ == '__main__':
    main()
