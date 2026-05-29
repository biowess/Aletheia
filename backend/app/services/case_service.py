from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.case import Case
from app.schemas.case import CaseCreateRequest, CaseUpdateRequest

class CaseServiceError(Exception):
    """Application-level exception for CaseService operations."""
    pass

class CaseService:
    """
    Architectural Notes:
    Service Layer vs Router Logic Separation:
    1. Separation of Concerns: The router is responsible for HTTP concerns (request parsing, response formatting, status codes), 
       while the service layer encapsulates business logic and database interactions.
    2. Reusability: By placing data access logic here, other parts of the application (e.g., background tasks, CLI commands) 
       can interact with cases without needing to mock HTTP requests or duplicate DB logic.
    3. Testability: Service methods can be easily unit-tested by providing a mocked database session, independent of the web framework.
    """

    @staticmethod
    async def create_case(db: AsyncSession, data: CaseCreateRequest) -> Case:
        try:
            case_data = data.model_dump(exclude_none=True)
            db_case = Case(**case_data)
            db.add(db_case)
            await db.commit()
            await db.refresh(db_case)
            return db_case
        except SQLAlchemyError as e:
            await db.rollback()
            raise CaseServiceError(f"Failed to create case: {str(e)}")

    @staticmethod
    async def get_case(db: AsyncSession, case_id: str) -> Case | None:
        try:
            stmt = select(Case).where(Case.id == case_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise CaseServiceError(f"Failed to retrieve case: {str(e)}")

    @staticmethod
    async def list_cases(db: AsyncSession, include_archived: bool = False) -> list[Case]:
        try:
            stmt = select(Case).order_by(desc(Case.created_at))
            if not include_archived:
                stmt = stmt.where(Case.is_archived == False)
                
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise CaseServiceError(f"Failed to list cases: {str(e)}")

    @staticmethod
    async def update_case(db: AsyncSession, case_id: str, data: CaseUpdateRequest) -> Case | None:
        try:
            stmt = select(Case).where(Case.id == case_id)
            result = await db.execute(stmt)
            db_case = result.scalar_one_or_none()
            
            if not db_case:
                return None
                
            update_data = data.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(db_case, key, value)
                
            await db.commit()
            await db.refresh(db_case)
            return db_case
        except SQLAlchemyError as e:
            await db.rollback()
            raise CaseServiceError(f"Failed to update case: {str(e)}")

    @staticmethod
    async def archive_case(db: AsyncSession, case_id: str) -> Case | None:
        try:
            stmt = select(Case).where(Case.id == case_id)
            result = await db.execute(stmt)
            db_case = result.scalar_one_or_none()
            
            if not db_case:
                return None
                
            db_case.is_archived = True
            await db.commit()
            await db.refresh(db_case)
            return db_case
        except SQLAlchemyError as e:
            await db.rollback()
            raise CaseServiceError(f"Failed to archive case: {str(e)}")

    @staticmethod
    async def unarchive_case(db: AsyncSession, case_id: str) -> Case | None:
        try:
            stmt = select(Case).where(Case.id == case_id)
            result = await db.execute(stmt)
            db_case = result.scalar_one_or_none()
            
            if not db_case:
                return None
                
            db_case.is_archived = False
            await db.commit()
            await db.refresh(db_case)
            return db_case
        except SQLAlchemyError as e:
            await db.rollback()
            raise CaseServiceError(f"Failed to unarchive case: {str(e)}")

    @staticmethod
    async def delete_case(db: AsyncSession, case_id: str) -> bool:
        try:
            stmt = select(Case).where(Case.id == case_id)
            result = await db.execute(stmt)
            db_case = result.scalar_one_or_none()
            
            if not db_case:
                return False
                
            await db.delete(db_case)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise CaseServiceError(f"Failed to delete case: {str(e)}")
