# Getting the Protocol Reviewed: Who, How, What to Send

**Status:** plan and draft email, not sent. The next input the project needs is a
human who has run a genetic toggle in *Bacillus subtilis* and used flow cytometry
on bacteria. No AI review changes what Experiment 1 will show.

## Who to ask (profile, not names)

Any one of these is enough for a first read:
- A graduate student or postdoc in a *B. subtilis* or synthetic biology lab who
  has built a fluorescent-reporter strain and run it on a flow cytometer.
- A staff scientist in a university flow cytometry or synthetic biology core
  facility. Core staff see failed bacterial cytometry every week and are often
  the best judges of the gating and instrument questions.
- A *Bacillus* researcher reached through a stock center or society. The
  Bacillus Genetic Stock Center (Ohio State University) is the usual source of
  strains and can point to who works with W168. Verify the current contact
  before writing.

Where to look, in order of ease: local universities with microbiology or
bioengineering departments (check department pages for people whose papers use
*B. subtilis* and fluorescence), the iGEM community, and corresponding authors of
*B. subtilis* synthetic biology papers. Do not cold-email the authors of the
closest prior art (Yang et al. 2020, Bonnet et al. 2012) first; if they are
approached at all it should be after the unfiled patent drafts have been looked at
by an attorney.

## Send exactly these three files, nothing else

1. `docs/PROTOCOL_REVIEW_HANDOFF.md`
2. `wet_lab_experiments/Experiment_1_Toggle_Confirmation.md`
3. `experiments/BENCH_PROTOCOL_BSUBTILIS.md` (Stage B0 section is what matters)

Do **not** attach the audit, the patent drafts (`patents/drafts_2026/`), the
manuscript or the pitch material. The three files above contain no draft claim
language. Check with the patent attorney whether even this level of sharing wants
a confidentiality agreement; the toggle idea itself is public prior art, the
damage-and-regrowth angle is the part not yet filed.

## Draft email (the founder signs it; edit freely)

Subject: Could you look over a *B. subtilis* toggle protocol? Ten minutes, no endorsement asked

Hello Dr. [name],

I'm Dayana Sanchez, founder of Acheron, a small research project. We are asking
whether a stored bit, held as the state of an engineered genetic toggle in
*B. subtilis*, survives damage and regrowth. Everything so far is simulation. No
bench result exists, and I would rather say that first.

Before we spend money on the first experiment, I would like a practitioner to tell
us what is wrong with the craft of the protocol: gating, the inducer calibration,
whether hysteresis can run in batch culture, sporulation control. I am not asking
you to endorse the project. The attached note lists the specific questions and the
values only a lab can set. It takes about ten minutes to read.

If you are not the right person, I would be grateful for a name. Thank you.

Dayana Sanchez
Founder, Acheron

## After the first reply

Record what they changed in `docs/PROTOCOL_REVIEW_HANDOFF.md` ("Reviewed by", date,
changes) and update Experiment 1 and Stage B0 together. Do not add detail from any
further AI review first.
