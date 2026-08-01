from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime
import os
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.student_profile import StudentProfile
from app.models.company_requirement import CompanyRequirement
from app.models.model_registry import ModelRegistry, ModelStatus
from app.schemas.admin import (
    CompanyRequirementCreate, CompanyRequirementUpdate, CompanyRequirementOut,
    ModelRegistryOut, ModelRetrainResponse, AdminAnalyticsOut
)
from app.schemas.profile import StudentProfileOut
from app.api.deps import get_current_admin
from app.services import dataset_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/students", response_model=List[StudentProfileOut])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    career_goal: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    query = db.query(StudentProfile)
    if department:
        query = query.filter(StudentProfile.department.ilike(f"%{department}%"))
    if career_goal:
        query = query.filter(StudentProfile.career_goal.ilike(f"%{career_goal}%"))
    
    profiles = query.offset(skip).limit(limit).all()
    return profiles

@router.get("/students/{id}", response_model=StudentProfileOut)
def get_student_detail(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    profile = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile

@router.post("/company-requirements", response_model=CompanyRequirementOut)
def create_company_requirement(
    req_in: CompanyRequirementCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    company_req = CompanyRequirement(
        company_name=req_in.company_name,
        role=req_in.role,
        required_skills=req_in.required_skills,
        min_cgpa=req_in.min_cgpa,
        notes=req_in.notes
    )
    db.add(company_req)
    db.commit()
    db.refresh(company_req)
    return company_req

@router.get("/company-requirements", response_model=List[CompanyRequirementOut])
def get_company_requirements(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    reqs = db.query(CompanyRequirement).all()
    if not reqs:
        # Seed and PERSIST default requirements on first use. Previously
        # these were constructed in-memory only and returned without being
        # saved — any later PUT /company-requirements/{id} against them
        # would 404 because the row never actually existed in the DB.
        seed = [
            CompanyRequirement(
                company_name="Google",
                role="Software Engineer (SDE I)",
                required_skills=["Python", "C++", "System Design", "Algorithms"],
                min_cgpa=8.5,
                notes="Targeting graduating batch 2025."
            ),
            CompanyRequirement(
                company_name="Amazon",
                role="Full Stack Developer",
                required_skills=["React", "Java", "AWS", "REST APIs"],
                min_cgpa=8.0,
                notes="Must have 1+ web dev internship."
            )
        ]
        db.add_all(seed)
        db.commit()
        for r in seed:
            db.refresh(r)
        reqs = seed
    return reqs

@router.put("/company-requirements/{id}", response_model=CompanyRequirementOut)
def update_company_requirement(
    id: int,
    req_in: CompanyRequirementUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    company_req = db.query(CompanyRequirement).filter(CompanyRequirement.id == id).first()
    if not company_req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

    update_data = req_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(company_req, field, val)

    db.commit()
    db.refresh(company_req)
    return company_req

@router.get("/dataset/info")
def get_dataset_info(
    admin: User = Depends(get_current_admin)
):
    return dataset_service.get_dataset_info()


@router.post("/dataset/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only .csv files are accepted.")
    contents = await file.read()
    try:
        info = dataset_service.validate_and_save_dataset(contents)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Dataset uploaded and validated successfully.", **info}


@router.post("/model/retrain", response_model=ModelRetrainResponse)
def retrain_model_trigger(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    try:
        result = dataset_service.retrain_model()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Retraining failed: {str(e)}")

    xgb_metrics = result["metrics"].get("XGBoost", {})
    registry_entry = ModelRegistry(
        model_name=result["model_name"],
        version=result["new_version"],
        status=ModelStatus.ACTIVE,
        trained_at=datetime.datetime.utcnow(),
        metrics={
            **xgb_metrics,
            "dataset_source": result["dataset_source"],
            "dataset_rows": result["dataset_rows"],
            "full_comparison": result["metrics"],
        }
    )
    # Only one ACTIVE model at a time — archive the previous one.
    db.query(ModelRegistry).filter(
        ModelRegistry.model_name == result["model_name"],
        ModelRegistry.status == ModelStatus.ACTIVE
    ).update({"status": ModelStatus.ARCHIVED})
    db.add(registry_entry)
    db.commit()

    return ModelRetrainResponse(
        message=f"Model retrained on {result['dataset_rows']} rows "
                f"({result['dataset_source']} dataset) and is now live.",
        model_name=result["model_name"],
        new_version=result["new_version"],
        status="active",
        metrics=xgb_metrics,
    )

@router.get("/model/registry", response_model=List[ModelRegistryOut])
def get_model_registry(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    models = db.query(ModelRegistry).order_by(ModelRegistry.trained_at.desc()).all()
    if not models:
        # Seed and PERSIST one real registry entry reflecting the model that
        # was actually trained at setup time, rather than fabricated metrics
        # for a model that was never registered in the DB.
        import json
        metrics_path = os.path.join(dataset_service.MODEL_DIR, "model_metrics.json")
        xgb_metrics = {}
        if os.path.exists(metrics_path):
            with open(metrics_path) as f:
                xgb_metrics = json.load(f).get("XGBoost", {})
        seed = ModelRegistry(
            model_name="PlacementXGBoostClassifier",
            version="v1-initial-synthetic",
            status=ModelStatus.ACTIVE,
            trained_at=datetime.datetime.utcnow(),
            metrics={**xgb_metrics, "dataset_source": "synthetic"}
        )
        db.add(seed)
        db.commit()
        db.refresh(seed)
        models = [seed]
    return models

@router.get("/analytics", response_model=AdminAnalyticsOut)
def get_admin_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    from app.models.readiness import ReadinessScore
    from app.models.resume import ResumeAnalysis
    from app.models.placement_prediction import PlacementPrediction
    from app.models.skill_gap import SkillGapResult
    from sqlalchemy import func, case

    total_students = db.query(StudentProfile).count()

    avg_readiness = db.query(func.avg(ReadinessScore.overall_readiness)).scalar()
    avg_ats = db.query(func.avg(ResumeAnalysis.ats_score)).scalar()
    avg_placement_prob = db.query(func.avg(PlacementPrediction.placement_probability)).scalar()
    industry_ready_count = db.query(PlacementPrediction).filter(
        PlacementPrediction.readiness_level == "industry_ready"
    ).count()

    # Top missing skills: flatten JSON arrays across all skill_gap_results
    # rows in Python, since counting elements inside a JSON array isn't
    # portable SQL across SQLite/MySQL without JSON_TABLE-style functions.
    skill_gap_rows = db.query(SkillGapResult.missing_skills).all()
    skill_counter: Dict[str, int] = {}
    for (missing_list,) in skill_gap_rows:
        for skill in (missing_list or []):
            skill_counter[skill] = skill_counter.get(skill, 0) + 1
    top_missing_skills = [
        {"skill": s, "count": c}
        for s, c in sorted(skill_counter.items(), key=lambda x: -x[1])[:8]
    ]

    dept_rows = (
        db.query(
            StudentProfile.department,
            func.count(StudentProfile.id),
            func.avg(ReadinessScore.overall_readiness),
        )
        .outerjoin(ReadinessScore, ReadinessScore.student_id == StudentProfile.id)
        .filter(StudentProfile.department.isnot(None))
        .group_by(StudentProfile.department)
        .all()
    )
    department_stats = [
        {
            "department": dept,
            "students": count,
            "avg_readiness": round(avg_r, 1) if avg_r is not None else None,
        }
        for dept, count, avg_r in dept_rows
    ]

    return AdminAnalyticsOut(
        total_students=total_students,
        avg_readiness_score=round(avg_readiness, 1) if avg_readiness is not None else 0.0,
        avg_ats_score=round(avg_ats, 1) if avg_ats is not None else 0.0,
        avg_placement_probability=round(avg_placement_prob, 4) if avg_placement_prob is not None else 0.0,
        industry_ready_count=industry_ready_count,
        top_missing_skills=top_missing_skills,
        department_stats=department_stats,
    )