# Acheron 101, Part 2: The Juicy Version

The same story as `ACHERON_101.md`, told like the best gossip you have ever
heard. Every juicy detail is real and comes from our own results, with the
receipts in `docs/SCIENTIFIC_AUDIT_2026.md`. Nothing here has been tested in a
lab yet. All of it is simulation, so read the gossip as "what the model says",
not "what the bacteria did".

`ACHERON_101.md` is still there, untouched, for the serious version.

---

## Episode 1: The Premise

Okay, so. The idea is wild. We want to write a 0 or a 1 into a living thing,
hurt it badly, and then see if the 0 or 1 is still there after it grows back.

Think of a hard drive that heals itself. You scratch it, and the scratch
repairs. Nobody has ever shown that this works. Not once. That is exactly why
we are poking at it.

---

## Episode 2: The Ex Who Broke Our Heart (the flatworms)

We started with planarian flatworms. Everything looked perfect. The bit stayed
put for a whole day. We were thrilled.

Then we added noise, the normal random jiggling that real life has. And the
perfect result fell apart. The bit turned into a coin flip. Heads, tails,
whatever. About 50 percent right, which is no better than guessing.

The first result only worked in a world with zero randomness, and there is no
such world. We did not hide it. We put the breakup in writing, in the audit, and
moved on.

Lesson: it was not the worm's fault. Our test was too good to be true.

---

## Episode 3: The New Crush (the bacteria switch)

Enter *B. subtilis*, a harmless little bacterium with a very boring, very
reliable personality. And we gave it a switch.

The switch is called a toggle. It is two genes in an arm-wrestling match. Each
gene makes a protein that mutes the other one. Whoever is winning keeps the
other muted, and the match stays that way until somebody flips it on purpose.
Winner A means 0. Winner B means 1.

Here is the first big tea: the match only works if the two arms are about equally
strong. If one arm is far stronger, the match is rigged, the same one wins
forever, and the switch is dead. It cannot store anything. We call that a
monostable dead switch. This is the biggest design rule we found: **match your
promoters or the switch dies.**

---

## Episode 4: The Exes Who Got There First (the prior art)

Plot twist, and we have to be honest about it. We are not the first people to
store a bit in a living cell.

- **Yang and friends (2020)** wrote patterns into bacteria with light, using
  voltage. But their memory is a temporary kind that gets lost when the cells
  divide.
- **Bonnet and friends (2012)** built a memory in the DNA itself. It survives
  division and can be flipped back and forth. Same trick we are trying, kind of.

So when somebody asks "is this new?", the honest answer is: parts of it, maybe.
What we have NOT shown is any advantage over Bonnet's DNA memory. We say that
out loud, every time. Our edge, if we have one, is the self-healing part: the
organism noticing the damage and repairing the data. That part is still a
proposal, not a result.

---

## Episode 5: The Noise Drama

Noise is the loud neighbor who ruins everything. We asked: how loud can the
neighbor get before the switch gives up?

Our first, simple answer was scary. The switch gave up after only a little more
noise. We nearly panicked.

Then we did what you do with a suspicious witness: we asked a second, more
careful witness. The careful one counts every single molecule, one at a time.
And it said: calm down, the switch is much tougher than the first witness
claimed.

Why did they disagree? The first witness was a drama queen. When a gene is almost
completely off, the simple method gets the numbers wrong and makes it look like
the gene is leaking. The molecule-by-molecule version does not have that
problem.

So now we trust the careful witness more. The scary result belonged to the
drama queen, not to the cells.

---

## Episode 6: We Caught Ourselves (the confessions)

Receipts time. While checking our own work we found three embarrassing things:

1. **The step-size bug.** The strength of the noise secretly changed depending
   on how small our time steps were. Like a scale that gives a different weight
   depending on how fast you step on it. We built a corrected version, ran our
   old results again, and they held up. We left the original file alone on
   purpose so nothing was lost.
2. **The wrong headline.** We had claimed our noise setting was 3 to 17 times
   too low. It turned out we had compared two things that cannot be compared,
   like comparing a speed to a weight. We took the claim back and marked it as
   withdrawn.
3. **A bad rule.** Our first way of telling a real switch from a fake one was
   wrong. It would have called a dead switch healthy. We caught it on the very
   first data, fixed it, and wrote down that we had been wrong.

Why tell you? Because the project's whole personality is: say the embarrassing
thing first.

---

## Episode 7: The Witnesses Agree (different math)

Here is the part that made us sit up. We checked the switch with completely
different math, pen-and-paper algebra, and the answers lined up. It agreed
with the simulation about where the switch works and where it dies, at 16 out of
16 settings.

But we must be fair. One person's assumptions went into all of it, so the math
agreeing means we were consistent. It does not mean real bacteria will behave.
Great gossip needs a reliable narrator, and we do not claim to be one.

---

## Episode 8: The Marble Split

When a cell divides, it has to share its molecules between the two daughters. It
is like splitting a handful of marbles between two kids by flipping a coin for
each marble. Somebody always gets a few more. Would that unfairness break the
memory?

We tested it. It did not. The switch survived the unfair splitting.

---

## Episode 9: The Headline (the 2 percent)

This is the big one. We damaged the colony until only 2 out of every 100 cells
were left. Then we let it regrow.

The result: in the simulation, almost every cell in the regrown colony still held
the right bit. About 98 to 100 percent.

Now the fine print, because the gossip is only good if it is true. This worked
**only if the survivors held the right bit to begin with.** If the survivors
are wrong, the whole colony inherits the wrong answer. A colony remembers
exactly what its survivors remember, no better.

---

## Episode 10: The Crowd (more than one bit)

One bit is cute. Data needs lots of them. So we asked: what if we put several
switches in the same cell?

Shocking twist: the number of molecules was not the problem. The problem was
leaking. If one switch's proteins leak onto the neighbors' controls even a
little, the switches start muting each other by accident. Like roommates who
keep accidentally using each other's remote. With eight switches, a leak of just
1 percent left only about a third of the messages intact.

So we tried a different plan: one switch per cell, spread over many cells, with
spare copies that vote. Like writing each letter five times and taking the
majority.

How long does that last, in the simulation? At the setting we tested:
- A short message with no protection: about 3 days before it is a coin flip
  whether something changed.
- With five copies of every bit: about 3 weeks.
- With the whole thing rewritten into fresh cells every few hours: a month or
  longer.

Rewriting needs a machine that reads and rewrites every cell. That is a big job,
and the numbers assume the machine makes no mistakes. And one thing no amount of
spare copies fixes: if something hits many cells at once, like contamination,
the copies all go down together.

---

## Episode 11: The Big Secret We Don't Know

Here is the tea nobody can spill yet, because nobody knows it: how fast a bit
flips by itself in a real cell. Every number about "how long" in this document
leans on a guess about that. Same for how many molecules a real cell holds.

The lab is the only one who can answer. That is the next episode.

---

## Episode 12: The Cliffhanger (what happens next)

The plot, in order. Each step can end the whole story:

1. **Pilot, then Experiment 1.** Does the switch really have two stable states
   in real bacteria? This is step zero.
2. **A microbiologist reads our plan** and tells us what we got wrong.
3. **Count the molecules** in real cells, so a guess becomes a number.
4. **Damage and regrowth.** The first real test of the Acheron idea.
5. **Self-detection of damage.** The wildest part of the pitch, and the least
   tested.

Passing step 1 does not prove Acheron. Only steps 4 and 5 would.

---

## The Cast List

- **Acheron:** the project. Wants to store a bit in something that heals.
- **The toggle:** two genes in an arm-wrestle. The star.
- **Promoter mismatch:** the rigged match that kills the star.
- **Noise:** the loud neighbor.
- **The careful witness:** the molecule-by-molecule model. Trustworthy.
- **The drama queen:** the simple noise model. Overreacts when a gene is almost off.
- **Yang 2020 and Bonnet 2012:** the exes who got there first.
- **Spare copies:** the same bit written several times, majority vote.
- **Rewriting:** copying the message into fresh cells before it fades.
- **The lab:** the only one who can end the gossip.

---

*Want it juicier, shorter, or about a different part? Tell me which episode and
I'll rewrite it.*
