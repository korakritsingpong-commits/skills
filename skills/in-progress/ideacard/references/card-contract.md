# Card contract: schema 3.0

The authoritative field types and enums are in `../scripts/card_models.py`. `knowledge-card.schema.json` is the generated JSON Schema. Do not alter these to fit a single subject.

Canonical wrapper: `{"cards": [KnowledgeCard, ...]}`. Emit every top-level card field, including empty arrays and explicit nulls. A new unanswered question has no answer, claims, sources, review date or answer IDs. Research may change its type and status without changing identity.

## Field roles

- `primary_question`: one question this card answers; `title`: readable page name.
- `scope`: context, things included/excluded, assumptions, optional jurisdiction and timeframe.
- `short_answer`: supported synthesis; `answer_claim_ids`: its supporting claim IDs.
- `claims`: atomic statements with type, evidence status, evidence references, reasoning and limitations.
- `sources`: inspected material, including version and provenance. IDs are local to the card.
- `open_questions`: genuinely unresolved subquestions, not placeholders for completed work.
- `relations`: directed links to other cards.
- `extensions`: domain-specific fields as labeled values with optional supporting claim IDs.
- `review_status`, `reviewed_at`, `review_triggers`: evidence review, not automated publication timestamps.

## Relation direction

Read every edge as **this card → relation → target card**:

- `ขยายความ`: this card elaborates the target. Use for a follow-up when the target is not necessarily a prerequisite.
- `ต้องเข้าใจก่อน`: the target is a prerequisite for understanding this card. The note must make that direction clear.
- `เป็นส่วนหนึ่งของ`: this card is part of the target.
- `เปรียบเทียบกับ`, `โต้แย้ง`, `นำไปใช้กับ`, `แทนที่`, `เกี่ยวข้องกับ`: ordinary directional meanings.

Use `relations` for derivation instead of adding `derived_from` to the JSON schema. Multiple edges are allowed when they express distinct useful relationships. Keep derivation notes explicit.

## Evidence rules

A hypothesis can exist before proof in a researched card if labeled accurately, but seed cards use `open_questions` instead of speculative claims. “มีหลักฐานสนับสนุน” means evidence exists, not certainty or consensus. Contradictory evidence must remain visible. Explain secondary-source limitations, partial retrieval, unclear versions and OCR uncertainty when material. `reviewed_at` is the actual review date, never a claim of completeness.

## Local checks versus content review

The validator checks structural and referential integrity. An agent still checks whether a cited passage supports the claim, the scope fits the question, uncertainty is honest, and follow-up questions are useful and nonduplicate. Passing validation does not establish factual accuracy.
