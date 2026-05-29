from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import ReportVersion

class ReportVersionService:
    """
    Service for managing report versions.
    
    Architectural Note: Immutability is enforced at the service layer by strictly
    omitting any update or delete methods. While the database layer might have
    some constraints (depending on dialect), handling it at the service layer
    ensures that the application's business logic fundamentally treats report
    versions as append-only, historical snapshots, preventing accidental 
    modifications throughout the application lifecycle.
    """

    @staticmethod
    async def create_report_version(db: AsyncSession, case_id: str, report_data: dict) -> ReportVersion:
        """
        Creates a new immutable report version.
        Determines the next version_number by querying the max version for the case_id.
        """
        stmt = select(func.max(ReportVersion.version_number)).where(ReportVersion.case_id == case_id)
        result = await db.execute(stmt)
        max_version = result.scalar()
        
        next_version = 1 if max_version is None else max_version + 1

        new_report = ReportVersion(
            case_id=case_id,
            version_number=next_version,
            **report_data
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return new_report

    @staticmethod
    async def get_report_version(db: AsyncSession, report_id: str) -> ReportVersion | None:
        """Fetches a report version by its primary key."""
        stmt = select(ReportVersion).where(ReportVersion.id == report_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_report_versions_for_case(db: AsyncSession, case_id: str) -> list[ReportVersion]:
        """Returns all versions for a case, ordered by version_number ascending."""
        stmt = select(ReportVersion).where(ReportVersion.case_id == case_id).order_by(ReportVersion.version_number.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_latest_report_version(db: AsyncSession, case_id: str) -> ReportVersion | None:
        """Returns the highest-version-number report for a case, or None if none exist."""
        stmt = select(ReportVersion).where(ReportVersion.case_id == case_id).order_by(ReportVersion.version_number.desc()).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
