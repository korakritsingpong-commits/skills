# Markdown reading view

Render from validated JSON, retaining IDs in frontmatter and explicit claim anchors in the body. Use:

1. YAML frontmatter: id, schema_version, type, topics, status, reviewed_at, jurisdiction.
2. Title and primary question.
3. Short answer; unanswered drafts say “ยังไม่ได้ค้นคำตอบ”.
4. Scope: context, applies to, exclusions, assumptions and timeframe when present.
5. Details: each claim, evidence status, limitations and reasoning when present. Link each source ID to its bibliography anchor and include the passage locator.
6. Open questions and how to resolve them.
7. Related cards with readable titles and directional relation notes. Link relative Markdown paths only for cards actually rendered in this bundle. Show unresolved external targets as IDs; a host wiki may resolve them separately.
8. Optional domain extensions.
9. Sources with publisher, version, date/access date and location.
10. Review date and review triggers when present.

Omit empty sections. A draft's empty answer is unanswered; an empty extensions list is not applicable; an inspected claim lacking evidence is insufficient evidence. Do not collapse these states into one “unknown”. In user-facing prose use the user's language. Quotes belong to exact excerpts; paraphrases belong to statements or notes.
