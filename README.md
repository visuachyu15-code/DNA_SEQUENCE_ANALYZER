# Longest Common DNA Substring

DAA Hackathon project — solved with **Dynamic Programming**.

## 1. Problem Statement
A bioinformatics system compares two DNA sequences to identify the longest continuous
DNA pattern common to both. Find the longest substring that occurs in both sequences.

## 2. Problem Understanding
- Input: two DNA strings made of `A`, `C`, `G`, `T`.
- "Continuous" means adjacent characters, so this is a **substring** problem.
- It is **not** Longest Common Subsequence (LCS), which may skip characters.

## 3. Input / Output (documented assumption)
The original statement does not fix a format, so we assume:

| | |
|---|---|
| Input | two DNA sequences `S1`, `S2` (one per line) |
| Output | the longest common substring and its length |
| Ties | return **all** longest substrings, each with its position |
| No common character | `None`, length `0` |
| Either input empty | `None`, length `0` |

No numeric constraints were given, so none are assumed.

## 4. Approach
`dp[i][j]` = length of the longest common substring ending exactly at `S1[i-1]` and `S2[j-1]`.
- If `S1[i-1] == S2[j-1]`: `dp[i][j] = dp[i-1][j-1] + 1`
- Otherwise: `dp[i][j] = 0` (a mismatch breaks continuity — this reset is what separates substring from LCS)

Track the maximum value and the end position in `S1`, then reconstruct with
`S1[end - max_len : end]`.

## 5. Pseudocode
```
LONGEST_COMMON_SUBSTRING(S1, S2)
    if S1 is empty OR S2 is empty: return None, 0
    n <- length(S1); m <- length(S2)
    create dp[0..n][0..m] filled with 0
    max_length <- 0; end_position <- 0
    for i <- 1 to n:
        for j <- 1 to m:
            if S1[i-1] = S2[j-1]:
                dp[i][j] <- dp[i-1][j-1] + 1
                if dp[i][j] > max_length:
                    max_length <- dp[i][j]; end_position <- i
            else:
                dp[i][j] <- 0
    if max_length = 0: return None, 0
    return S1[end_position - max_length : end_position], max_length
```

## 6. Complexity
- **Time:** O(n × m) — every pair of characters is compared once.
- **Space:** O(n × m) for the 2D table. `longest_common_substring_optimized()` keeps only the previous row, giving **O(m)** space.

## 7. Sample Run
```
Enter DNA sequence 1: ACGTAC
Enter DNA sequence 2: TTACGA
Longest Common Substring: ACG, TAC
Length: 3
Similarity: 50.0% of the shorter sequence
  ACG  found at index 0 in S1 and 2 in S2
  TAC  found at index 3 in S1 and 1 in S2
```
Note: this example has two answers of length 3 (a tie), and both are reported.

## 7a. Features
- All tied longest substrings, with 0-based positions in both sequences
- FASTA / text file input: `python main.py --fasta sample.fasta sample2.fasta`
- Input cleanup (lowercase, spaces, newlines) and A/C/G/T validation
- Similarity % (common length / shorter sequence length)
- Performance comparison: `python main.py --bench` (time and peak memory, O(nm) vs O(m) space)
- Web UI: open `index.html` in a browser (no server, no install). Paste or load FASTA, see highlighted matches and the DP table.

## 8. Edge Cases Covered
Normal match, ties, no common character, identical strings, one/both strings empty,
single-character strings, match at beginning / middle / end, shorter string is the
whole answer, ties between equal-length substrings, non-DNA characters rejected.

## 9. How to Run
```bash
python main.py                                   # interactive
python main.py --fasta sample.fasta sample2.fasta  # from files
python main.py --bench                           # performance comparison
python run_tests.py                              # 21/21 checks pass
# web UI: double-click index.html
```
Requires Python 3.6+. No external libraries.

## 10. Files
```
main.py          DP solution (standard + space-optimized), FASTA, benchmark, CLI
index.html       web UI (same algorithm in JavaScript)
run_tests.py     automated test runner
test_cases.txt   test cases table
sample.fasta, sample2.fasta   example input files
screenshots/     test output and UI screenshots
```
