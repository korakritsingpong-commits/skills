"""KnowledgeCard 3.0; Pydantic 2. No domain-specific required fields."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Source(Model):
    source_id: str
    title: str
    source_type: Literal['เอกสาร','เว็บไซต์','งานวิจัย','ชุดข้อมูล','การสัมภาษณ์','การสังเกต/การทดลอง','บันทึกภายใน','อื่นๆ']
    creators: list[str] = Field(default_factory=list)
    publisher: str | None = None
    url: str | None = None
    resource_ref: str | None = None
    published_at: str | None = None
    accessed_at: date
    version: str | None = None

class Evidence(Model):
    source_id: str
    locator: str | None = None
    excerpt: str | None = None
    relation: Literal['สนับสนุน','โต้แย้ง','ให้บริบท']
    note: str | None = None

class Claim(Model):
    claim_id: str
    statement: str
    claim_type: Literal['นิยาม','ข้อเท็จจริง','ข้อวิเคราะห์','สมมติฐาน','ข้อเสนอแนะ']
    evidence_status: Literal['มีหลักฐานสนับสนุน','มีหลักฐานขัดแย้ง','หลักฐานยังไม่เพียงพอ','ยังไม่ได้ตรวจสอบ','ไม่ใช่ข้อกล่าวอ้างเชิงประจักษ์']
    evidence: list[Evidence] = Field(default_factory=list)
    reasoning: str | None = None
    limitations: list[str] = Field(default_factory=list)

class KnowledgeScope(Model):
    context: str
    applies_to: list[str] = Field(default_factory=list)
    excludes: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    jurisdiction: str | None = None
    temporal_scope: str | None = None

class OpenQuestion(Model):
    question: str
    significance: str
    resolution_method: str | None = None

class CardRelation(Model):
    target_card_id: str
    relation: Literal['ขยายความ','เป็นส่วนหนึ่งของ','ต้องเข้าใจก่อน','เปรียบเทียบกับ','โต้แย้ง','นำไปใช้กับ','แทนที่','เกี่ยวข้องกับ']
    note: str | None = None

class DetailItem(Model):
    label: str
    value: str
    claim_ids: list[str] = Field(default_factory=list)

class KnowledgeExtension(Model):
    extension_type: str
    items: list[DetailItem]

class KnowledgeCard(Model):
    schema_version: Literal['3.0'] = '3.0'
    card_id: str = Field(pattern=r'^[a-z0-9][a-z0-9_-]*$')
    title: str
    card_type: Literal['นิยาม','คำอธิบาย','วิธีทำ','การเปรียบเทียบ','ข้อค้นพบ','การตัดสินใจ','ไอเดีย','คำถามเปิด']
    primary_question: str
    short_answer: str
    answer_claim_ids: list[str]
    topics: list[str]
    scope: KnowledgeScope
    claims: list[Claim]
    sources: list[Source]
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    relations: list[CardRelation] = Field(default_factory=list)
    extensions: list[KnowledgeExtension] = Field(default_factory=list)
    review_status: Literal['ร่าง','ตรวจสอบบางส่วน','ตรวจสอบตามขอบเขตแล้ว','ต้องทบทวน']
    reviewed_at: date | None = None
    review_triggers: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def check_integrity(self):
        sources = {s.source_id for s in self.sources}
        claims = {c.claim_id for c in self.claims}
        if len(sources) != len(self.sources) or len(claims) != len(self.claims):
            raise ValueError('Duplicate source_id or claim_id')
        if not set(self.answer_claim_ids) <= claims:
            raise ValueError('Unresolved answer_claim_ids')
        for c in self.claims:
            if any(e.source_id not in sources for e in c.evidence):
                raise ValueError(f'Unresolved evidence source in {c.claim_id}')
            expected = {'มีหลักฐานสนับสนุน': 'สนับสนุน', 'มีหลักฐานขัดแย้ง': 'โต้แย้ง'}.get(c.evidence_status)
            if expected and not any(e.relation == expected for e in c.evidence):
                raise ValueError(f'{c.claim_id}: evidence status requires {expected} evidence')
        for extension in self.extensions:
            if any(not set(item.claim_ids) <= claims for item in extension.items):
                raise ValueError('Unresolved extension claim_ids')
        if self.card_type == 'คำถามเปิด' and self.review_status == 'ร่าง':
            if self.short_answer or self.answer_claim_ids or self.claims or self.sources or self.reviewed_at:
                raise ValueError('Unanswered draft must have empty answer/evidence and null reviewed_at')
        if self.short_answer and not self.answer_claim_ids:
            raise ValueError('An answer must reference claims')
        if self.review_status in ['ตรวจสอบบางส่วน','ตรวจสอบตามขอบเขตแล้ว'] and not self.reviewed_at:
            raise ValueError('Reviewed cards require reviewed_at')
        if any(r.target_card_id == self.card_id for r in self.relations):
            raise ValueError('Self relations are not allowed')
        return self

class KnowledgeResponse(Model):
    cards: list[KnowledgeCard]

    @model_validator(mode='after')
    def unique_ids(self):
        ids = [c.card_id for c in self.cards]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate card_id')
        return self
