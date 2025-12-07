import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.schemas import FinalReview
from src.graph.workflow import ReviewOrchestrator
from src.rag.knowledge_base import KnowledgeBaseBuilder
from src.models.db import SessionLocal, ReviewModel

router = APIRouter(prefix="/api")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Models
class FileReviewRequest(BaseModel):
    file_path: str

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = "snippet"

class GithubPRRequest(BaseModel):
    repo: str
    pr_number: int
    github_token: Optional[str] = None

# Logic
orchestrator = ReviewOrchestrator()

@router.post("/review/file", response_model=FinalReview)
def review_file_endpoint(req: FileReviewRequest, db: Session = Depends(get_db)):
    try:
        result = orchestrator.review_file(req.file_path)
        _save_review(db, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review/code", response_model=FinalReview)
def review_code_endpoint(req: CodeReviewRequest, db: Session = Depends(get_db)):
    try:
        result = orchestrator.review_code(req.code, req.language, req.filename)
        _save_review(db, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews", response_model=List[dict])
def list_reviews(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    reviews = db.query(ReviewModel).offset(skip).limit(limit).all()
    # Simple serialization helper
    return [{"id": r.id, "file_path": r.file_path, "score": r.overall_score, "date": r.created_at} for r in reviews]

@router.get("/review/{review_id}")
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post("/knowledge-base/rebuild")
def rebuild_knowledge_base(background_tasks: BackgroundTasks):
    builder = KnowledgeBaseBuilder()
    background_tasks.add_task(builder.build)
    return {"status": "started", "message": "Knowledge Base rebuild triggered in background"}

def _save_review(db: Session, review: FinalReview):
    """Helper to save review to DB"""
    db_obj = ReviewModel(
        file_path=review.file_path,
        overall_score=review.overall_score,
        summary=review.summary,
        findings=[f.dict() for f in review.all_findings]
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

# Simplified GitHub PR Stub (Full implementation requires GitHub API client logic)
@router.post("/review/github-pr")
def review_github_pr(req: GithubPRRequest):
    return {"status": "not_implemented", "message": "GitHub PR review logic requires PyGithub or similar integration."}

# WebSocket for streaming (Skeleton)
@router.websocket("/ws/review")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Here we would parse request and hook into LangGraph streaming events
            # For now, just echo
            await websocket.send_text(f"Received: {data}")
    except Exception:
        pass
