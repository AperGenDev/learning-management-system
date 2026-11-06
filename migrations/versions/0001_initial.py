"""initial schema: roles, users, categories, courses, modules, enrollments

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-02 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role_id", sa.BigInteger(),
            sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index("ix_users_role_id", "users", ["role_id"])

    op.create_table(
        "courses",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "author_id", sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False,
        ),
        sa.Column(
            "category_id", sa.BigInteger(),
            sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index("ix_courses_author_id", "courses", ["author_id"])
    op.create_index("ix_courses_category_id", "courses", ["category_id"])

    op.create_table(
        "modules",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "course_id", sa.BigInteger(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.UniqueConstraint("course_id", "order_num", name="uq_module_order"),
    )
    op.create_index("ix_modules_course_id", "modules", ["course_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "student_id", sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "course_id", sa.BigInteger(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "enrolled_at", sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])


def downgrade() -> None:
    op.drop_table("enrollments")
    op.drop_table("modules")
    op.drop_table("courses")
    op.drop_table("users")
    op.drop_table("categories")
    op.drop_table("roles")
