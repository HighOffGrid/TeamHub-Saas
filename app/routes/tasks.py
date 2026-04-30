from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import Task, User, Project, Membership
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter()

def _check_project_access(user_id: str, project_id: str, session: Session):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = session.exec(
        select(Membership).where(
            Membership.organization_id == project.organization_id,
            Membership.user_id == user_id,
        )
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    return project, membership

@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user),):
    _check_project_access(current_user.id, payload.project_id, session)
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("", response_model=list[TaskOut])
def list_tasks(project_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user),):
    _check_project_access(current_user.id, project_id, session)
    tasks = session.exec(select(Task).where(Task.project_id == project_id)).all()
    return tasks

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user),):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _check_project_access(current_user.id, task.project_id, session)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user),):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _check_project_access(current_user.id, task.project_id, session)
    session.delete(task)
    session.commit()