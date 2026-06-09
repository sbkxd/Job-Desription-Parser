"""Repositories package — exports all repository classes."""

from app.repositories.base import AbstractRepository, SQLAlchemyRepository
from app.repositories.job_repository import JobRepository
from app.repositories.skill_repository import SkillRepository

__all__ = [
    "AbstractRepository",
    "SQLAlchemyRepository",
    "JobRepository",
    "SkillRepository",
]
