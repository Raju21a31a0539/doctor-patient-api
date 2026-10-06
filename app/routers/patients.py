from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient, User
from ..schemas import (
    PatientCreate,
    PatientResponse
)

from ..dependencies import (
    get_current_user
)

from ..services.patient_service import (
    create_patient,
    get_all_patients,
    get_patient
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "",
    response_model=PatientResponse
)
def create_patient_api(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return create_patient(
        db,
        patient_data.name,
        patient_data.age,
        patient_data.phone
    )


@router.get(
    "",
    response_model=list[PatientResponse]
)
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Admin can see all patients.
    if current_user.role == "admin":

        return get_all_patients(db)

    # Doctor can only see their own patients.
    doctor = db.query(
        __import__(
            "app.models",
            fromlist=["Doctor"]
        ).Doctor
    ).filter(
        __import__(
            "app.models",
            fromlist=["Doctor"]
        ).Doctor.email == current_user.email
    ).first()

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    return db.query(Patient).filter(
        Patient.doctor_id == doctor.id
    ).all()


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    patient = get_patient(
        db,
        patient_id
    )

    if patient is None:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Admin can view any patient.
    if current_user.role == "admin":
        return patient

    # Doctor must own the patient.
    from ..models import Doctor

    doctor = db.query(Doctor).filter(
        Doctor.email == current_user.email
    ).first()

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    if patient.doctor_id != doctor.id:

        raise HTTPException(
            status_code=403,
            detail="You can only view your own patients"
        )

    return patient