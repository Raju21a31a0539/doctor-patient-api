from sqlalchemy.orm import Session

from ..models import Patient


def create_patient(
    db: Session,
    name: str,
    age: int,
    phone: str
):

    patient = Patient(
        name=name,
        age=age,
        phone=phone
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def get_all_patients(
    db: Session
):

    return db.query(Patient).all()


def get_patient(
    db: Session,
    patient_id: int
):

    return db.query(Patient).filter(
        Patient.id == patient_id
    ).first()


def assign_patient_to_doctor(
    db: Session,
    patient: Patient,
    doctor_id: int
):

    patient.doctor_id = doctor_id

    db.commit()
    db.refresh(patient)

    return patient


def get_doctor_patients(
    db: Session,
    doctor_id: int
):

    return db.query(Patient).filter(
        Patient.doctor_id == doctor_id
    ).all()