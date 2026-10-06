from sqlalchemy.orm import Session

from ..models import Doctor


def create_doctor(
    db: Session,
    name: str,
    specialization: str,
    email: str
):

    doctor = Doctor(
        name=name,
        specialization=specialization,
        email=email
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def get_all_doctors(
    db: Session
):

    return db.query(Doctor).filter(
        Doctor.is_active == True
    ).all()


def get_doctor(
    db: Session,
    doctor_id: int
):

    return db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()


def update_doctor(
    db: Session,
    doctor: Doctor,
    name=None,
    specialization=None,
    email=None
):

    if name is not None:
        doctor.name = name

    if specialization is not None:
        doctor.specialization = specialization

    if email is not None:
        doctor.email = email

    db.commit()
    db.refresh(doctor)

    return doctor


def soft_delete_doctor(
    db: Session,
    doctor: Doctor
):

    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor