"""Render validated knowledge cards to Markdown. Existing outputs are replaced."""
import argparse
import json
from pathlib import Path
from card_models import KnowledgeResponse

def render(card, local):
    q = lambda value: json.dumps(value, ensure_ascii=False)
    meta = {'id':card.card_id,'schema_version':card.schema_version,'type':card.card_type,'topics':card.topics,'status':card.review_status,'reviewed_at':str(card.reviewed_at) if card.reviewed_at else None,'jurisdiction':card.scope.jurisdiction}
    parts = ['---\n'+'\n'.join(f'{key}: {q(value)}' for key,value in meta.items())+'\n---',f'# {card.title}',f'> **คำถาม:** {card.primary_question}',card.short_answer or 'ยังไม่ได้ค้นคำตอบ']
    if card.answer_claim_ids:
        parts.append('ข้อกล่าวอ้างที่รองรับคำตอบ: '+', '.join(f'[{i}](#claim-{i})' for i in card.answer_claim_ids))
    scope = [card.scope.context]
    for label,items in [('ครอบคลุม',card.scope.applies_to),('ไม่ครอบคลุม',card.scope.excludes),('สมมติฐาน',card.scope.assumptions)]:
        if items: scope.append(f'**{label}:**\n\n'+'\n'.join('- '+x for x in items))
    if card.scope.temporal_scope: scope.append('ช่วงเวลาที่กล่าวถึง: '+card.scope.temporal_scope)
    parts += ['## ขอบเขต', '\n\n'.join(scope)]
    if card.claims:
        parts.append('## รายละเอียดและหลักฐาน')
        for c in card.claims:
            parts += [f'<a id="claim-{c.claim_id}"></a>',f'### {c.claim_id}',c.statement,f'ประเภท: {c.claim_type} · หลักฐาน: {c.evidence_status}']
            if c.reasoning: parts.append('เหตุผล: '+c.reasoning)
            for e in c.evidence:
                parts.append(f'- [{e.source_id}](#source-{e.source_id}) — {e.relation}'+(' · '+e.locator if e.locator else '')+(' · '+e.note if e.note else ''))
                if e.excerpt: parts.append('> '+e.excerpt.replace('\n','\n> '))
            if c.limitations: parts.append('ข้อจำกัด:\n\n'+'\n'.join('- '+x for x in c.limitations))
    if card.open_questions:
        parts.append('## เรื่องที่ยังต้องค้น')
        for question in card.open_questions:
            parts += ['- **'+question.question+'**',question.significance]
            if question.resolution_method: parts.append('วิธีค้น: '+question.resolution_method)
    if card.relations:
        parts.append('## ความรู้ที่เกี่ยวข้อง')
        for r in card.relations:
            target = f'[{local[r.target_card_id]}]({r.target_card_id}.md)' if r.target_card_id in local else f'`{r.target_card_id}` (การ์ดภายนอกชุดนี้)'
            parts.append(f'- {target}: {r.relation}'+(' — '+r.note if r.note else ''))
    for extension in card.extensions:
        parts.append('## '+extension.extension_type)
        for item in extension.items:
            parts.append(f'**{item.label}:** {item.value}'+(' ('+', '.join(f'[{i}](#claim-{i})' for i in item.claim_ids)+')' if item.claim_ids else ''))
    if card.sources:
        parts.append('## แหล่งอ้างอิง')
        for s in card.sources:
            parts += [f'<a id="source-{s.source_id}"></a>',f'### {s.source_id}: {s.title}']
            if s.creators: parts.append('ผู้สร้าง: '+', '.join(s.creators))
            if s.publisher: parts.append('ผู้เผยแพร่: '+s.publisher)
            if s.url: parts.append('[เปิดต้นทาง]('+s.url+')')
            if s.resource_ref: parts.append('ทรัพยากร: '+s.resource_ref)
            if s.published_at: parts.append('เผยแพร่: '+s.published_at)
            parts.append('เข้าถึง: '+str(s.accessed_at))
            if s.version: parts.append('รุ่น/ข้อจำกัด: '+s.version)
    if card.reviewed_at: parts.append('ตรวจสอบล่าสุด: '+str(card.reviewed_at))
    if card.review_triggers: parts.append('ทบทวนเมื่อ:\n\n'+'\n'.join('- '+x for x in card.review_triggers))
    return '\n\n'.join(parts)+'\n'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    bundle = KnowledgeResponse.model_validate_json(args.input.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    local = {c.card_id:c.title for c in bundle.cards}
    for c in bundle.cards:
        (args.out/(c.card_id+'.md')).write_text(render(c,local))
    print(f'Rendered {len(bundle.cards)} cards to {args.out}')

if __name__ == '__main__':
    main()
