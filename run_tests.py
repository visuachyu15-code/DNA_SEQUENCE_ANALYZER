"""Runs all test cases against both DP versions, plus extra checks."""
import os
import random
import tempfile

from main import (find_all, find_all_optimized, brute_force_length,
                  longest_common_substring, clean, validate_dna, read_fasta)

# (s1, s2, expected_length, expected set of distinct longest substrings)
TESTS = [
    ("ACGTAC", "TTACGA", 3, {"ACG", "TAC"}),   # tie: the worked example has two answers
    ("ACGT", "TTACG", 3, {"ACG"}),
    ("AAAA", "CCCC", 0, set()),
    ("ACGT", "ACGT", 4, {"ACGT"}),
    ("A", "A", 1, {"A"}),
    ("A", "C", 0, set()),
    ("ACGT", "CG", 2, {"CG"}),
    ("ACG", "TACGTT", 3, {"ACG"}),
    ("", "ACGT", 0, set()),
    ("ACGT", "", 0, set()),
    ("", "", 0, set()),
    ("AACCGGTT", "CCGG", 4, {"CCGG"}),
    ("ACGTTT", "ACGAAA", 3, {"ACG"}),
    ("TTTACG", "AAAACG", 3, {"ACG"}),
    ("AAATTT", "TTTAAA", 3, {"AAA", "TTT"}),   # tie: BOTH are returned now
]

failed = 0


def check(name, ok):
    global failed
    print(("PASS  " if ok else "FAIL  ") + name)
    failed += (not ok)


for k, (s1, s2, exp_len, exp_subs) in enumerate(TESTS, 1):
    ok = True
    for fn in (find_all, find_all_optimized):
        length, matches = fn(s1, s2)
        ok &= length == exp_len and {m[0] for m in matches} == exp_subs
        # every reported position must really point at the substring
        ok &= all(s1[a:a + length] == sub == s2[b:b + length] for sub, a, b in matches)
    check("case %02d  %-9s %-9s -> %s" % (k, s1 or "(empty)", s2 or "(empty)", sorted(exp_subs) or "None"), ok)

# positions
length, matches = find_all("ACGTAC", "TTACGA")
check("positions: ACG (0,2) and TAC (3,1) reported", sorted(matches) == [("ACG", 0, 2), ("TAC", 3, 1)])

# backward-compatible helper
check("longest_common_substring() still returns (sub, len)", longest_common_substring("ACGTAC", "TTACGA") == ("ACG", 3))  # first one found

# cleanup / validation
check("clean() handles lowercase and whitespace", clean(" acg t\nac ") == "ACGTAC")
check("validate_dna() rejects non-ACGT", validate_dna("ACGT") and not validate_dna("ACXT"))

# FASTA
with tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False) as f:
    f.write(">seq1\nACGT\nacgt\n>seq2\nTTTT\n")
seqs = read_fasta(f.name)
os.unlink(f.name)
check("read_fasta() joins wrapped lines and splits records", seqs == ["ACGTACGT", "TTTT"])

# random cross-check against brute force
random.seed(1)
ok = True
for _ in range(2000):
    a = "".join(random.choice("ACGT") for _ in range(random.randint(0, 12)))
    b = "".join(random.choice("ACGT") for _ in range(random.randint(0, 12)))
    r1, r2 = find_all(a, b), find_all_optimized(a, b)
    ok &= r1 == r2 and r1[0] == brute_force_length(a, b)
check("2000 random pairs: both DP versions == brute force", ok)

total = len(TESTS) + 6
print("\n%d/%d checks passed" % (total - failed, total))
