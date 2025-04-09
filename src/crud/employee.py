from typing import Optional, List
from sqlmodel import Session, select
from src.models.employee import Employee, EmployeeCreate, EmployeeUpdate
from src.config.security import get_password_hash, verify_password
from .base import CRUDBase

class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_by_email(self, session: Session, *, email: str) -> Optional[Employee]:
        return session.exec(select(Employee).where(Employee.email == email)).first()

    def get_by_enterprise(
        self, 
        session: Session, 
        *, 
        enterprise_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        return session.exec(
            select(Employee)
            .where(Employee.enterprise_id == enterprise_id)
            .offset(skip)
            .limit(limit)
        ).all()

    def create(self, session: Session, *, obj_in: EmployeeCreate) -> Employee:
        db_obj = Employee(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            name=obj_in.name,
            lastname=obj_in.lastname,
            code=obj_in.code,
            telephone=obj_in.telephone,
            enterprise_id=obj_in.enterprise_id,
            role_id=obj_in.role_id,
            is_active=True
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def authenticate(self, session: Session, *, email: str, password: str) -> Optional[Employee]:
        employee = self.get_by_email(session=session, email=email)
        if not employee:
            return None
        if not verify_password(password, employee.hashed_password):
            return None
        return employee

    def update(self, session: Session, *, db_obj: Employee, obj_in: EmployeeUpdate) -> Employee:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(session=session, db_obj=db_obj, obj_in=update_data)

employee = CRUDEmployee(Employee)