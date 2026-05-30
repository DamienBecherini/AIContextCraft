---
name: External plan intake policy update
overview: Update the AIContextCraft Cursor rule to require verification of pasted external AI plans and generation of an improved self-contained plan before any save prompt, with commit proposal only after the report-append question is answered.
todos:
  - id: read-existing-rule
    content: Confirm current AIContextCraft rule structure to preserve all existing guidance
    status: pending
  - id: draft-external-plan-section
    content: Draft new section requiring verification and self-contained rewrite of external plans
    status: pending
  - id: merge-with-existing-policy
    content: Integrate section without altering existing parts (publication, report persistence, commit proposal, tests)
    status: pending
  - id: validate-final-rule
    content: Review and verify full flow coherence before save prompt
    status: pending
  - id: publish-plan-copy-step
    content: Include plan copy step in docs/plans/ with normalized timestamped name
    status: pending
isProject: false
---

# Update external plan handling guidance

## Objective

Add a rule section that forces the agent to:

- analyze a plan pasted from another AI,
- verify coherence/completeness,
- generate a **self-contained** corrected/improved plan if needed (without referencing the source plan),
- keep existing guidance, with explicit order: report-append question first, then commit message proposal.

The existing rule is preserved and extended in [`/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc).

## Planned changes

- Add a new section (e.g. `## External Plan Intake and Self-Contained Rewrite`) in [`/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc).
- Define the mandatory flow explicitly:
  1. detect that an external plan was provided/pasted,
  2. validate quality/risks/gaps,
  3. produce a new self-contained plan (no mention of the original plan),
  4. integrate relevant corrections/improvements,
  5. ask the plan save/publication question if applicable,
  6. after implementation, ask whether to append the report to the plan,
  7. only after the user's answer to that question, propose the commit message.
- Specify minimum validation criteria (clarity, feasibility, execution order, tests/validation, risks, dependencies).
- Ensure compatibility with existing rules (publication question, report persistence, commit message proposal, Python test procedure), locking order “append question → user answer → commit proposal”.

## Verification

- Re-read the modified rule to confirm no existing guidance was removed.
- Verify the sequence “self-contained rewrite before save prompt” is unambiguous and prioritized when an external plan is pasted.
- Verify commit proposal never appears before the user answers the report-append question.

## Plan publication (requested)

- Copy the validated plan into `docs/plans/`.
- Rename to `YYYY_MM_DD_HH-MM_<branch-slug>_<plan-title>.plan.md` with ASCII kebab-case title.

---
## Implementation report

### Changes made

- Added section `## External Plan Intake and Self-Contained Rewrite` in `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`.
- This section requires analyzing an external plan, rewriting it as a self-contained plan without reference to the source, and improving/correcting it when relevant.
- Commit section reinforced to require strict order: report-append question → user answer → commit message proposal.

### Modified files

- `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`
- `/opt/AIContextCraft/docs/plans/2026_05_17_17-43_main_maj-consigne-plan-externe.plan.md`

### Validation

- Full rule review to verify existing guidance is preserved.
- Flow coherence verified: external plan → self-contained plan → confirmation.
- Explicit order constraint verified for commit proposal.
- Linter check via `ReadLints`: no errors.
