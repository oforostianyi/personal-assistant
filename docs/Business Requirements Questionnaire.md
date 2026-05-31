# Personal Assistant

# Business Requirements Interview Notes

**Subject matter:** Context-aware console Personal Assistant for contacts, notes, tags, birthdays, local persistence, and demo data.

**Stakeholder:** Python course project team, team lead, course curator/evaluator, and end users who need a lightweight offline personal information manager.

**Interview date:** 2026-05-31

## Q1. What business problem are you trying to solve, or what business opportunity do you perceive?

Users need one offline terminal application to organize contacts, birthdays, notes, tags, and note-contact links. The course team also needs a complete, demonstrable Python project with clear architecture and review evidence.

## Q2. What is the motivation for solving this problem or pursuing this opportunity?

The main pain points are scattered personal data, manual lookup, lost notes between sessions, and hard-to-use command-line tools. The updated project addresses this with contextual navigation, entity views, tab completion, fuzzy suggestions, and local persistence.

## Q3. What are your business objectives?

The product must support contacts, notes, tags, birthdays, search, persistence, context-aware help, demo seed data, and easy local launch commands.

## Q4. How would the proposed product provide value?

For users, the value is faster local lookup and editing. For the course evaluator, the value is visible evidence of Python design: domain models, validation, context-aware command registration, persistence, UI rendering, and integration through PRs.

## Q5. What would a highly successful solution do?

A successful solution runs from a fresh clone, can load demo data, supports a full walkthrough across `contacts`, `notes`, and `tags`, saves changes on exit, and relaunches with data intact.

## Q6. How could you judge success?

Success is judged by README walkthrough completion, syntax checks, seed-data sanity checks, manual end-to-end demo, and consistency between code, README, and requirements documents.

## Q7. What is the impact if the solution is not completed?

The team would not satisfy the final project requirements, and users would continue managing related personal data across separate manual tools.

## Q8. Who is affected by this project?

Affected parties: end users, course curator/evaluator, team lead, contacts/notes/tags/UI module owners, GitHub PR workflow, Trello board, and local filesystem storage.

## Q9. What are the timing goals or constraints?

The repository now includes the integrated hierarchical design and final demo support. Requirements must track the current `main` branch before presentation and defense materials are finalized.

## Q10. What should the team do differently from earlier attempts?

The current product uses context-aware navigation, module/entity prompts, and entity-enter behavior. Documentation must describe this implemented design consistently.

## Q11. What assumptions and risks remain?

Key assumptions: local Python environment, terminal use, single-user offline storage, pickle persistence, and manual smoke verification. Key risks: stale documentation, stale pickle data, seed loader overwriting user data when `--force` is used, and final presentation diverging from the current README behavior.
