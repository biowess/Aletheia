from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.follow_up_entry import FollowUpEntry
from app.schemas.follow_up_entry import FollowUpCreateRequest

class FollowUpService:
    """
    Service for managing follow-up entries for clinical cases.
    
    Architectural Notes:
    - Append-Only: Follow-up entries represent distinct chronological events. They are 
      immutable after creation to preserve an exact history. No delete or general update 
      methods are provided here.
    - Controlled Mutation: The only mutation allowed is linking a follow-up to a generated 
      report version (`triggered_report_id`), which happens after the reasoning engine 
      completes its asynchronous task.
    """

    @staticmethod
    async def create_follow_up(db: AsyncSession, case_id: str, data: FollowUpCreateRequest) -> FollowUpEntry:
        entry = FollowUpEntry(
            case_id=case_id,
            entry_type=data.entry_type,
            title=data.title,
            anamnesis_delta=data.anamnesis_delta.model_dump(exclude_none=True) if data.anamnesis_delta else {},
            physical_exam_delta=data.physical_exam_delta.model_dump(exclude_none=True) if data.physical_exam_delta else {},
            laboratory_delta=data.laboratory_delta.model_dump(exclude_none=True) if data.laboratory_delta else {},
            morphological_delta=data.morphological_delta.model_dump(exclude_none=True) if data.morphological_delta else {},
            free_text_note=data.free_text_note,
            triggered_report_id=None
        )
        
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def get_follow_up(db: AsyncSession, entry_id: str) -> FollowUpEntry | None:
        result = await db.execute(select(FollowUpEntry).where(FollowUpEntry.id == entry_id))
        return result.scalars().first()

    @staticmethod
    async def list_follow_ups_for_case(db: AsyncSession, case_id: str) -> list[FollowUpEntry]:
        result = await db.execute(
            select(FollowUpEntry)
            .where(FollowUpEntry.case_id == case_id)
            .order_by(FollowUpEntry.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def link_follow_up_to_report(db: AsyncSession, entry_id: str, report_id: str) -> FollowUpEntry | None:
        entry = await FollowUpService.get_follow_up(db, entry_id)
        if not entry:
            return None
            
        entry.triggered_report_id = report_id
        await db.commit()
        await db.refresh(entry)
        return entry
