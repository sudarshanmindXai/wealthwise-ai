import re

text = """
Part B (Annexure)
Details of Salary paid and any other income and tax deducted

1. Gross Salary
   (a) Salary as per provisions contained in section 17(1)                          45,00,000
   (b) Value of perquisites under section 17(2)                                     0
   (c) Profits in lieu of salary under section 17(3)                                0
   Total                                                                            45,00,000
"""

pattern_old = r"\(a\)\s+[Ss]alary.*?(\d{1,3}(?:,\d{2,3})*)"
# New: Optionally consume "17(d)" and require spacing?
# Actually simple fix: Require at least 2 spaces before the amount if possible, 
# OR just skip "17(1)" explicitly.
pattern_new = r"\(a\)\s+[Ss]alary(?:.*?17\(\d\))?.*?(\d{1,3}(?:,\d{2,3})*)"

match_old = re.search(pattern_old, text, re.DOTALL)
match_new = re.search(pattern_new, text, re.DOTALL)

print(f"Old Match: {match_old.group(1) if match_old else 'None'}")
print(f"New Match: {match_new.group(1) if match_new else 'None'}")

# Verify correctness
expected = "45,00,000"
if match_new and match_new.group(1) == expected:
    print("SUCCESS: Regex fix verified.")
else:
    print("FAILURE: Regex fix failed.")
