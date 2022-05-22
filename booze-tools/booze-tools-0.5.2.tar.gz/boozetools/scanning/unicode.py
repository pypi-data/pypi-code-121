"""
For now, this is a placeholder module.

Eventually, I want to address concerns for Unicode-correctness in scanning.
Scanner tables should not re-encode any fraction of the Unicode database,
but should instead consult the existing one for any character where it matters.

The first concern is how to represent, and sensibly combine, all conceivable character classes,
in such a way that they do the right thing without bloating your automaton.

It begins with a Unicode-savvy model of an arbitrary character class.
This must be a Boolean formula involving characters, ranges, and Unicode properties.
Normalize these formulas into a form where each section is concerned with a different
categorization of code points.

It will probably be smart, in the context of a unicode scanner, to do a first pass over all definitions
to work out all reasonable character class distinctions and cases. This turns into a primary finite alphabet.
Ideally, represent this as a minimal decision tree and then enumerate each node.
Any specific character class becomes a subset of these enumerated nodes.
Having that, the remainder of the NFA/DFA logic works in the usual manner.
The tricky bit at the end is to convert everything into something that can run reasonably fast.

Suppose we handle codepoints 0-127 as in normal ASCII. The Unicode properties of these characters
are etched in stone, so the quick indexing operation is just fine.
Suppose also non-ASCII characters are ineligible as range endpoints,
which is acceptable in Unicode mode. Then the reader can have a simple algorithm:
If the input character is ASCII, consult a classical table.
Otherwise, consult the Unicode database and follow a state-specific decision tree.

The key is keeping the decision-tree both sensible and balanced. For example,
anything with a language tag won't have a number type, so there's no point
having a decision-tree node where both apply. But this kind of smarts takes a
careful reading of the standard.

It's probably not feasible to try to build everything out at once.
Maybe start with support for general character categories, which have a well-defined alphabet.
This would probably get most of the real use-cases.
"""