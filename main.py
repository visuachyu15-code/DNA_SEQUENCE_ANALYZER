"""
Longest Common DNA Substring  (DAA Hackathon)  -  Dynamic Programming

dp[i][j] = length of the longest common substring ENDING at s1[i-1] and s2[j-1].
  match    -> dp[i][j] = dp[i-1][j-1] + 1
  mismatch -> dp[i][j] = 0        (continuity is broken)

Time : O(n*m)   Space: O(n*m)  (find_all_optimized uses O(m))
Quick wins: all tied answers, match positions, FASTA input, input cleanup,
            performance comparison (--bench).
"""
import argparse
import random
import time
import tracemalloc

VALID_BASES = set("ACGT")


def clean(seq):
    """Upper-case and drop spaces / newlines / tabs."""
    return "".join(seq.split()).upper()


def validate_dna(seq):
    """True if seq has only A, C, G, T (empty is allowed)."""
    return all(ch in VALID_BASES for ch in seq)


def read_fasta(path):
    """Return the sequences found in a FASTA (or plain text) file."""
    seqs, cur = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if cur:
                    seqs.append(clean("".join(cur)))
                cur = []
            elif line:
                cur.append(line)
    if cur:
        seqs.append(clean("".join(cur)))
    return seqs


def find_all(s1, s2):
    """
    Standard 2D DP. Returns (length, matches).
    matches = every occurrence of a maximum-length common substring as
    (substring, start_in_s1, start_in_s2), 0-based. Empty list when length is 0.
    """
    if not s1 or not s2:
        return 0, []
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best, ends = 0, []
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best:
                    best, ends = dp[i][j], [(i, j)]
                elif dp[i][j] == best:
                    ends.append((i, j))
            else:
                dp[i][j] = 0
    if best == 0:
        return 0, []
    return best, [(s1[i - best:i], i - best, j - best) for i, j in ends]


def find_all_optimized(s1, s2):
    """Same result as find_all, but O(m) space (keeps only the previous row)."""
    if not s1 or not s2:
        return 0, []
    n, m = len(s1), len(s2)
    prev = [0] * (m + 1)
    best, ends = 0, []
    for i in range(1, n + 1):
        curr = [0] * (m + 1)
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1] + 1
                if curr[j] > best:
                    best, ends = curr[j], [(i, j)]
                elif curr[j] == best:
                    ends.append((i, j))
        prev = curr
    if best == 0:
        return 0, []
    return best, [(s1[i - best:i], i - best, j - best) for i, j in ends]


def brute_force_length(s1, s2):
    """O(n^2 * m) reference used only for benchmarking and cross-checks."""
    best = 0
    for i in range(len(s1)):
        for j in range(i + 1, len(s1) + 1):
            if j - i > best and s1[i:j] in s2:
                best = j - i
    return best


def longest_common_substring(s1, s2):
    """Backward-compatible: (first longest substring or None, length)."""
    length, matches = find_all(s1, s2)
    return (matches[0][0], length) if matches else (None, 0)


def similarity(s1, s2, length):
    """Common substring length as % of the shorter sequence."""
    shorter = min(len(s1), len(s2))
    return round(100 * length / shorter, 1) if shorter else 0.0


def print_result(s1, s2):
    length, matches = find_all(s1, s2)
    if not matches:
        print("Longest Common Substring: None\nLength: 0")
        return
    distinct = sorted({m[0] for m in matches})
    print("Longest Common Substring:", ", ".join(distinct))
    print("Length:", length)
    print("Similarity: %s%% of the shorter sequence" % similarity(s1, s2, length))
    for sub, a, b in matches:
        print("  %s  found at index %d in S1 and %d in S2" % (sub, a, b))


def benchmark():
    """Time and peak memory of both DP versions as the input size doubles."""
    random.seed(7)
    print("Benchmark: random DNA, n = m  (time grows ~4x when n doubles -> O(n*m))")
    print("  %-6s %-24s %-24s" % ("n", "O(n*m) space", "O(m) space"))
    for n in (500, 1000, 2000):
        a = "".join(random.choice("ACGT") for _ in range(n))
        b = "".join(random.choice("ACGT") for _ in range(n))
        cells = []
        for fn in (find_all, find_all_optimized):
            tracemalloc.start()
            t = time.perf_counter()
            fn(a, b)
            ms = (time.perf_counter() - t) * 1000
            peak = tracemalloc.get_traced_memory()[1] / 1024
            tracemalloc.stop()
            cells.append("%7.0f ms %8.0f KB" % (ms, peak))
        print("  %-6d %-24s %-24s" % (n, cells[0], cells[1]))


def main():
    ap = argparse.ArgumentParser(description="Longest Common DNA Substring")
    ap.add_argument("--fasta", nargs=2, metavar=("FILE1", "FILE2"),
                    help="read one sequence from each FASTA/text file")
    ap.add_argument("--bench", action="store_true", help="run the performance comparison")
    args = ap.parse_args()

    if args.bench:
        benchmark()
        return
    if args.fasta:
        a, b = read_fasta(args.fasta[0]), read_fasta(args.fasta[1])
        if not a or not b:
            print("Could not find a sequence in one of the files.")
            return
        s1, s2 = a[0], b[0]
    else:
        s1 = clean(input("Enter DNA sequence 1: "))
        s2 = clean(input("Enter DNA sequence 2: "))

    if not validate_dna(s1) or not validate_dna(s2):
        print("Invalid input: DNA sequences may contain only A, C, G, T.")
        return
    print_result(s1, s2)


if __name__ == "__main__":
    main()
