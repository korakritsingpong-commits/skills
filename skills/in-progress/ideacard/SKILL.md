---
name: ideacard
description: Build an LLM wiki through structured question-first knowledge cards. Use when the user asks for ideacards, ไอเดียการ์ด, fundamental follow-up questions, researched knowledge cards, or JSON-to-Markdown wiki cards. Create schema 3.0 question cards before research, update the same cards with evidence, then derive the next fundamental questions. Supports any knowledge domain.
---

# Ideacard

Turn a topic into a traceable learning path: **question card → research → answered card → Markdown → next question cards**. Here an “idea” normally means a question worth investigating, rather than a commercial product idea. Follow explicit user requests when they want business ideas instead.

Use the user's language. One card addresses one coherent question and makes sense independently. JSON is the source of truth; Markdown is its reading view.

## Choose the requested operation

- **Seed:** turn a topic into one or more fundamental question cards. Stop before research when the user asks only for cards or questions.
- **Answer:** research an existing card and update its original `card_id`.
- **Extend:** derive fundamental follow-up question cards from an answered card. Preserve the parent.
- **Full cycle:** answer a card and create the next question cards when both are requested. Research only the selected card, leaving new children unanswered.
- **Render:** generate Markdown from existing JSON without silently changing its meaning or evidence.

Infer topic, scope, language, quantity and selected operation from the conversation and existing cards. Honor an explicit quantity. If none is given, generate up to five useful nonduplicate follow-ups; produce fewer if the remaining questions are redundant. Ask only when ambiguity materially changes the work; otherwise state a reasonable scope and proceed.

## 1. Establish the card before searching

Read `references/card-contract.md` and use `scripts/card_models.py` for schema 3.0. Read the relevant existing cards and index, if provided. Reuse existing IDs rather than creating duplicate questions.

For a new question, create and persist a complete draft JSON before the first retrieval call (or show it in chat if files are unavailable). Include:

- Stable `card_id`, title, `primary_question`, topics and a scope that separates relevant meanings, jurisdictions and timeframes.
- `card_type: "คำถามเปิด"`, `review_status: "ร่าง"`, `reviewed_at: null`.
- Empty `short_answer`, `answer_claim_ids`, `claims`, and `sources`.
- Open questions describing what must be found, why it matters and how to investigate.
- Directional relations to any parent or prerequisite cards.

A draft is a research intention, not a guessed answer. Existing source cards may inform the question; add sources to the new card only when using them as evidence for its own claims. Preserve a before-research snapshot when researching a draft so the sequence is inspectable.

**Done:** the selected question exists in the agreed structure with scope and unanswered research questions, and IDs have been checked for duplicates.

## 2. Research within that scope

Use available retrieval tools and applicable research skills. Respect offline/no-browsing instructions. Prefer primary sources appropriate to the field: statutes and issuing agencies for law, original studies for scientific findings, official documentation for APIs, or supplied observations and datasets. Inspect the relevant passages, not just search snippets.

Record the source, creator/publisher, URL or resource reference, version, actual access date, and locator. Preserve exact quotations only in `excerpt`; place paraphrases in statements or notes. A successful fetch or recent access date does not establish current legal validity or scientific consensus.

Track contradictions and missing information. For classification/count questions, establish the classification criterion first: distinguish regulatory groups, ingredient categories and nutrition groups, for example. Do not combine counts from different systems. Match the breadth of a conclusion to the breadth of evidence actually inspected.

**Done:** each answer-bearing claim has inspected support, or its uncertainty is explicitly recorded. If sources cannot be retrieved, retain a draft or partial result with the blocker; never invent citations or fill a likely answer as verified.

## 3. Update the original card

Keep its `card_id` and history/links. Write a direct `short_answer` and link it through `answer_claim_ids` to atomic claims. Label each claim as definition, fact, analysis, hypothesis or recommendation; separately label evidence status. Explain inference and limitations. Evidence can support, contradict or provide context; a context-only citation is not proof.

Select the answered card type (definition, explanation, comparison, procedure, finding, decision or idea). Remove resolved open questions; retain unresolved ones with their significance. Set `reviewed_at` to the real review date and select review status honestly. “ตรวจสอบตามขอบเขตแล้ว” means checked within the declared scope, not universal truth. Retain “ตรวจสอบบางส่วน” if a central subquestion, version check or relevant source remains unverified.

Use optional `extensions` for domain-specific details with links to supporting claim IDs. Business models, clearance pathways and market timelines belong there only when relevant. Do not add new top-level schema fields without an explicit schema change.

**Done:** the short answer is supported by its referenced claims; claim and source IDs resolve; remaining uncertainty is visible.

## 4. Derive the next fundamental questions

Generate questions from gaps or concepts introduced by the answer: definitions, distinctions, classification criteria, mechanisms, prerequisites or boundaries. For each candidate:

1. Explain why it follows from the parent.
2. Check it is not already answered in the parent or an existing card.
3. Limit it to a coherent searchable question and explicit scope.
4. Instantiate a full schema 3.0 draft before doing any research for it.
5. Link to its parent and any actual prerequisites using the relation rules.

Example: “อาหารคืออะไร” → “อาหารมีกี่ประเภทตามกฎหมายไทย” → “อาหารควบคุมเฉพาะต่างจากอาหารที่กำหนดมาตรฐานอย่างไร”. The children's empty answer and evidence fields indicate that they are a research queue. Avoid claiming a chain of questions is an established chain of facts.

**Done:** the requested number of useful question cards exists, with parent links and no premature answers.

## 5. Validate, render and deliver

Run from the skill directory, or substitute its absolute path:

```sh
python scripts/validate_cards.py /path/to/knowledge-cards.json
python scripts/render_cards.py /path/to/knowledge-cards.json --out /path/to/cards
```

Requires Python 3.10+ and Pydantic 2. If unavailable, perform equivalent checks manually and report that limitation; do not claim a script passed. Validate dates, enums, duplicate IDs and internal references. External relations are permitted but must be reported as external, not represented as locally available files.

Read `references/markdown.md` for rendering rules. Omit empty reading sections; preserve the distinction between an unanswered question, insufficient evidence and an irrelevant field. Retain claim-level traceability without exposing every JSON field in the prose.

Save the canonical JSON, rendered Markdown and question cards when file access is available. Default to `llm-wiki/` in the current project; use an existing wiki location or explicit user path instead. Preserve unrelated data and update only selected cards. Keep snapshots outside the canonical cards list. In the final response link outputs, state the key answer and material limits, and list follow-up questions. Do not require the user to read raw JSON to understand the result.
