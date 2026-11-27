import math

def wilson(k, n, z=1.96):
    """95% Wilson confidence interval for k successes out of n."""
    p = k / n
    centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(0, centre - half), min(1, centre + half)

def mcnemar_exact(b, c):
    """Exact two-sided McNemar test from discordant pair counts b and c."""
    n = b + c
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, p)

# 95% Wilson confidence intervals
for k in [25, 24, 23, 20, 19, 16]:
    lo, hi = wilson(k, 25)
    print(f"{k}/25: {lo:.1%} - {hi:.1%}")

# Exact McNemar tests on LLaMA paired accuracy (b = PSV right only, c = other right only)
for name, b, c in [("vs Baseline", 2, 0), ("vs CoT", 9, 0), ("vs Placebo", 6, 0)]:
    print(f"PSV {name}: {b + c} discordant pairs, p = {mcnemar_exact(b, c):.4f}")

# Lenient scoring: one discordant pair per comparison
print(f"Lenient, PSV vs each: 1 discordant pair, p = {mcnemar_exact(1, 0):.4f}")