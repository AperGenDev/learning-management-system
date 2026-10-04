from sqlalchemy import select
from database import SessionLocal
from models import Role, User, Category, Course, Module, Enrollment
from sqlalchemy.orm import selectinload


def create_role(name: str, description: str | None = None) -> Role:
    with SessionLocal() as session:
        role = Role(name=name, description=description)
        session.add(role)
        session.commit()
        session.refresh(role)
        return role
    
def get_role_by_name(name: str) -> Role | None:
    with SessionLocal() as session:
        return session.execute(
            select(Role).where(Role.name == name)
        ).scalar_one_or_none()

def get_role_by_id(role_id: int) -> Role | None:
    with SessionLocal() as session:
        return session.get(Role, role_id)

def get_all_roles() -> list[Role]:
    with SessionLocal() as session:
        return list(session.execute(select(Role)).scalars().all())


def create_user(full_name: str, email: str, password_hash: str, role_name: str) -> User:
    with SessionLocal() as session:
        role = session.execute(
            select(Role).where(Role.name == role_name)
        ).scalar_one_or_none()
        if role is None:
            raise ValueError(
                f"Роль '{role_name}' не найдена. "
                f"Сначала создай её через create_role()."
            )

        user = User(full_name=full_name, email=email, password_hash=password_hash, role_id=role.id)
        session.add(user)
        session.commit()
        session.refresh(user) 
        return user

def get_user_by_id(user_id: int) -> User | None:
    with SessionLocal() as session:
        stmt = (
            select(User).options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return session.execute(stmt).scalar_one_or_none()


def get_user_by_email(email: str) -> User | None:
    with SessionLocal() as session:
        stmt = select(User).options(selectinload(User.role)).where(User.email == email)
        return session.execute(stmt).scalar_one_or_none()

def get_all_users() -> list[User]:
    with SessionLocal() as session:
        stmt = select(User).options(selectinload(User.role))
        return list(session.execute(stmt).scalars().all())

def update_user(user_id: int, **fields) -> User | None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            return None
        
        role_name = fields.pop("role_name", None)
        if role_name is not None:
            role = session.execute(
                select(Role).where(Role.name == role_name)
            ).scalar_one_or_none()
            if role is None:
                raise ValueError(f"Роль '{role_name}' не найдена.")
            user.role_id = role.id
        
        for key, value in fields.items():
            setattr(user, key, value)
        session.commit()
        stmt = (
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return session.execute(stmt).scalar_one_or_none()


def delete_user(user_id: int) -> bool:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user is None:
            return False
        session.delete(user)
        session.commit()
        return True



def create_category(name: str, description: str | None = None) -> Category:
    with SessionLocal() as session:
        category = Category(name=name, description=description)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category


def get_all_categories() -> list[Category]:
    with SessionLocal() as session:
        return list(session.execute(select(Category)).scalars().all())


def delete_category(category_id: int) -> bool:
    with SessionLocal() as session:
        category = session.get(Category, category_id)
        if category is None:
            return False
        session.delete(category)
        session.commit()
        return True



def create_course(
    title: str,
    author_id: int,
    description: str | None = None,
    category_id: int | None = None,
    is_published: bool = False,
) -> Course:
    with SessionLocal() as session:
        course = Course(
            title=title,
            description=description,
            author_id=author_id,
            category_id=category_id,
            is_published=is_published,
        )
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


def get_course_by_id(course_id: int) -> Course | None:
    with SessionLocal() as session:
        return session.get(Course, course_id)


def get_courses_catalog(category_id: int | None = None) -> list[Course]:

    with SessionLocal() as session:
        stmt = select(Course).where(Course.is_published == True)
        if category_id is not None:
            stmt = stmt.where(Course.category_id == category_id)
        return list(session.execute(stmt).scalars().all())


def update_course(course_id: int, **fields) -> Course | None:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return None
        for key, value in fields.items():
            setattr(course, key, value)
        session.commit()
        session.refresh(course)
        return course


def delete_course(course_id: int) -> bool:
    with SessionLocal() as session:
        course = session.get(Course, course_id)
        if course is None:
            return False
        session.delete(course)  
        session.commit()
        return True



def create_module(course_id: int, title: str, order_num: int, content: str | None = None) -> Module:
    with SessionLocal() as session:
        module = Module(course_id=course_id, title=title, order_num=order_num, content=content)
        session.add(module)
        session.commit()
        session.refresh(module)
        return module


def get_modules_by_course(course_id: int) -> list[Module]:

    with SessionLocal() as session:
        stmt = select(Module).where(Module.course_id == course_id).order_by(Module.order_num)
        return list(session.execute(stmt).scalars().all())


def update_module(module_id: int, **fields) -> Module | None:
    with SessionLocal() as session:
        module = session.get(Module, module_id)
        if module is None:
            return None
        for key, value in fields.items():
            setattr(module, key, value)
        session.commit()
        session.refresh(module)
        return module


def delete_module(module_id: int) -> bool:
    with SessionLocal() as session:
        module = session.get(Module, module_id)
        if module is None:
            return False
        session.delete(module)
        session.commit()
        return True



def enroll_student(student_id: int, course_id: int) -> Enrollment | None:
    with SessionLocal() as session:
        stmt = select(Enrollment).where(
            Enrollment.student_id == student_id, Enrollment.course_id == course_id
        )
        existing = session.execute(stmt).scalar_one_or_none()
        if existing is not None:
            return None  
        
        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        session.add(enrollment)
        session.commit()
        session.refresh(enrollment)
        return enrollment


def get_my_courses(student_id: int) -> list[Course]:

    with SessionLocal() as session:
        stmt = (
            select(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == student_id)
        )
        return list(session.execute(stmt).scalars().all())


def get_students_of_course(course_id: int) -> list[User]:
    with SessionLocal() as session:
        stmt = (
            select(User)
            .join(Enrollment, Enrollment.student_id == User.id)
            .where(Enrollment.course_id == course_id)
            .options(selectinload(User.role)) 
        )
        return list(session.execute(stmt).scalars().all())


def delete_enrollment(enrollment_id: int) -> bool:
    with SessionLocal() as session:
        enrollment = session.get(Enrollment, enrollment_id)
        if enrollment is None:
            return False
        session.delete(enrollment)
        session.commit()
        return True
