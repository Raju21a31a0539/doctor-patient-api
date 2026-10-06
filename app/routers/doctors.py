from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Doctor, User
from ..schemas import (
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate,
    PatientResponse
)

from ..dependencies import (
    get_current_user,
    require_admin
)

from ..services.doctor_service import (
    create_doctor,
    get_all_doctors,
    get_doctor,
    update_doctor,
    soft_delete_doctor
)

from ..services.patient_service import (
    assign_patient_to_doctor,
    get_doctor_patients
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "",
    response_model=DoctorResponse
)
def create_doctor_api(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    existing_doctor = db.query(Doctor).filter(
        Doctor.email == doctor_data.email
    ).first()

    if existing_doctor:

        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    return create_doctor(
        db,
        doctor_data.name,
        doctor_data.specialization,
        doctor_data.email
    )


@router.get(
    "",
    response_model=list[DoctorResponse]
)
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_all_doctors(db)


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    doctor = get_doctor(
        db,
        doctor_id
    )

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    doctor = get_doctor(
        db,
        doctor_id
    )

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return update_doctor(
        db,
        doctor,
        doctor_data.name,
        doctor_data.specialization,
        doctor_data.email
    )


@router.delete(
    "/{doctor_id}"
)
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    doctor = get_doctor(
        db,
        doctor_id
    )

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    soft_delete_doctor(
        db,
        doctor
    )

    return {
        "message": "Doctor soft deleted successfully"
    }


@router.post(
    "/{doctor_id}/patients/{patient_id}",
    response_model=PatientResponse
)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    doctor = get_doctor(
        db,
        doctor_id
    )

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    from ..models import Patient

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return assign_patient_to_doctor(
        db,
        patient,
        doctor_id
    )


@router.get(
    "/{doctor_id}/patients",
    response_model=list[PatientResponse]
)
def get_doctors_patients(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    doctor = get_doctor(
        db,
        doctor_id
    )

    if doctor is None:

        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Doctors can only see their own patients.
    if current_user.role == "doctor":

        doctor_user = db.query(Doctor).filter(
            Doctor.email == current_user.email
        ).first()

        if doctor_user is None:
            raise HTTPException(
                status_code=404,
                detail="Doctor profile not found"
            )

        if doctor_user.id != doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own patients"
            )

    return get_doctor_patients(
        db,
        doctor_id
    )