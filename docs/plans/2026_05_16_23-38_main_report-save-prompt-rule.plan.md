---
name: report-save-prompt-rule
overview: Add an always-on Cursor rule in AIContextCraft that asks at the end of implementation whether the chat report should be saved to the plan file.
todos:
  - id: update-aicc-rule
    content: Extend plan-publication-policy.mdc in AIContextCraft with report-save guidance
    status: completed
  - id: validate-rule-structure
    content: Verify frontmatter and clarity of mandatory instructions
    status: completed
  - id: publish-generated-plan
    content: Publish validated plan under docs/plans/ with timestamped rename
    status: in_progress
isProject: false
---

# Add implementation report save prompt

## Objective
Set up an always-on Cursor rule in `AIContextCraft` that requires at the end of implementation:
- explicitly asking whether the implementation report shown in chat should be saved,
- if the user answers yes, appending it to the plan file with a clear separator between plan and report.

## Target files
- Rule to extend: [`/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`](/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc)

## Implementation plan
1. **Extend the AIContextCraft rule**
   - Keep the current policy (plan publication + test procedure).
   - Add a “Post-implementation report persistence” section that requires:
     - showing the report in chat at the end of execution,
     - asking the user whether to save it,
     - on yes, appending to the plan with an explicit separator (e.g. `---` then `## Implementation report`).

2. **Quick rule validation**
   - Verify `.mdc` frontmatter (`description`, `alwaysApply: true`) and readability.
   - Verify unambiguous flow: mandatory user question before any report save.

3. **Plan publication (requested)**
   - Add a publication step during execution:
     - copy the validated plan into `docs/plans/`,
     - rename to `YYYY_MM_DD_HH-MM_<branch-slug>_<plan-title>.plan.md` (ASCII kebab-case).

## Expected outcome
- The AIContextCraft repo has a Cursor rule that forces the end-of-implementation save question.
- If the user confirms, the report is appended to the plan with clear separation.
- The work plan is also published under `docs/plans/` with a timestamped name.

---

## Implementation report

Implementation completed; all plan todos are done for AIContextCraft.

- Rule `plan-publication-policy.mdc` extended in `AIContextCraft` with `Post-Implementation Report Persistence`.
- Flow now requires: show report in chat, ask for confirmation, save to plan only on yes.
- Append format specified in the rule: separator `---`, title `## Implementation report`, then report content.

### Modified files

- `/opt/AIContextCraft/.cursor/rules/plan-publication-policy.mdc`
- `/opt/AIContextCraft/docs/plans/2026_05_16_23-38_main_report-save-prompt-rule.plan.md`

### Validation

- Full rule review to confirm existing guidance is preserved.
- Rule content verified for AIContextCraft-specific usage.
