from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.models import Category, Course, Enrollment, Module, Role, User


# ROLES 

def create_role(session: Session, name: str, description: str | None = None) -> Role:
    role = Role(name=name, description=description)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


def get_role_by_name(session: Session, name: str) -> Role | None:
    return session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()


def get_role_by_id(session: Session, role_id: int) -> Role | None:
    return session.get(Role, role_id)


def get_all_roles(session: Session) -> list[Role]:
    return list(session.execute(select(Role)).scalars().all())


# USERS 

def create_user(session: Session, full_name: str, email: str, password_hash: str, role_name: str) -> User:
    role = get_role_by_name(session, role_name)
    if role is None:
        raise ValueError(f"Роль '{role_name}' не найдена. Сначала создай её через create_role().")

    user = User(full_name=full_name, email=email, password_hash=password_hash, role_id=role.id)
    session.add(user)
    session.commit()
    return get_user_by_id(session, user.id)


def get_user_by_id(session: Session, user_id: int) -> User | None:
    stmt = select(User).options(selectinload(User.role)).where(User.id == user_id)
    return session.execute(stmt).scalar_one_or_none()


def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).options(selectinload(User.role)).where(User.email == email)
    return session.execute(stmt).scalar_one_or_none()


def get_all_users(session: Session) -> list[User]:
    stmt = select(User).options(selectinload(User.role)).order_by(User.id)
    return list(session.execute(stmt).scalars().all())


def update_user(session: Session, user_id: int, **fields) -> User | None:
    user = session.get(User, user_id)
    if user is None:
        return None

    role_name = fields.pop("role_name", None)
    if role_name is not None:
        role = get_role_by_name(session, role_name)
        if role is None:
            raise ValueError(f"Роль '{role_name}' не найдена.")
        user.role_id = role.id

    for key, value in fields.items():
        setattr(user, key, value)
    session.commit()
    session.expire(user)  # сбрасываем кэш связи role, чтобы перечитать новую роль
    return get_user_by_id(session, user_id)


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True


#CATEGORIES 

def create_category(session: Session, name: str, description: str | None = None) -> Category:
    category = Category(name=name, description=description)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_category_by_id(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def get_category_by_name(session: Session, name: str) -> Category | None:
    return session.execute(select(Category).where(Category.name == name)).scalar_one_or_none()


def get_all_categories(session: Session) -> list[Category]:
    return list(session.execute(select(Category).order_by(Category.name)).scalars().all())


def delete_category(session: Session, category_id: int) -> bool:
    category = session.get(Category, category_id)
    if category is None:
        return False
    session.delete(category)
    session.commit()
    return True


# COURSES

def create_course(
    session: Session,
    title: str,
    author_id: int,
    description: str | None = None,
    category_id: int | None = None,
    is_published: bool = False,
) -> Course:
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


def get_course_by_id(session: Session, course_id: int) -> Course | None:
    return session.get(Course, course_id)


def get_courses_catalog(session: Session, category_id: int | None = None) -> list[Course]:
    """Каталог опубликованных курсов, опционально с фильтром по категории (сценарий 3)."""
    stmt = select(Course).where(Course.is_published.is_(True))
    if category_id is not None:
        stmt = stmt.where(Course.category_id == category_id)
    return list(session.execute(stmt.order_by(Course.id)).scalars().all())


def get_courses_by_author(session: Session, author_id: int) -> list[Course]:
    stmt = select(Course).where(Course.author_id == author_id).order_by(Course.id)
    return list(session.execute(stmt).scalars().all())


def get_courses_by_ids(session: Session, course_ids: list[int]) -> dict[int, Course]:
    if not course_ids:
        return {}
    stmt = select(Course).where(Course.id.in_(course_ids))
    return {course.id: course for course in session.execute(stmt).scalars().all()}


def get_course_student_counts(session: Session) -> dict[int, int]:
    """Сколько студентов записано на каждый курс: {course_id: количество}."""
    stmt = select(Enrollment.course_id, func.count(Enrollment.id)).group_by(Enrollment.course_id)
    return {course_id: count for course_id, count in session.execute(stmt).all()}


def update_course(session: Session, course_id: int, **fields) -> Course | None:
    course = session.get(Course, course_id)
    if course is None:
        return None
    for key, value in fields.items():
        setattr(course, key, value)
    session.commit()
    session.refresh(course)
    return course


def delete_course(session: Session, course_id: int) -> bool:
    course = session.get(Course, course_id)
    if course is None:
        return False
    session.delete(course)  # каскадно удалит модули и записи на курс
    session.commit()
    return True


# MODULES

def create_module(session: Session, course_id: int, title: str, order_num: int, content: str | None = None) -> Module:
    module = Module(course_id=course_id, title=title, order_num=order_num, content=content)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module


def get_module_by_id(session: Session, module_id: int) -> Module | None:
    return session.get(Module, module_id)


def get_modules_by_course(session: Session, course_id: int) -> list[Module]:
    """Структура курса — модули по порядку (сценарий 5)."""
    stmt = select(Module).where(Module.course_id == course_id).order_by(Module.order_num)
    return list(session.execute(stmt).scalars().all())


def update_module(session: Session, module_id: int, **fields) -> Module | None:
    module = session.get(Module, module_id)
    if module is None:
        return None
    for key, value in fields.items():
        setattr(module, key, value)
    session.commit()
    session.refresh(module)
    return module


def delete_module(session: Session, module_id: int) -> bool:
    module = session.get(Module, module_id)
    if module is None:
        return False
    session.delete(module)
    session.commit()
    return True


# ENROLLMENTS

def get_enrollment(session: Session, student_id: int, course_id: int) -> Enrollment | None:
    stmt = select(Enrollment).where(
        Enrollment.student_id == student_id, Enrollment.course_id == course_id
    )
    return session.execute(stmt).scalar_one_or_none()


def enroll_student(session: Session, student_id: int, course_id: int) -> Enrollment | None:
    """Запись студента на курс (сценарий 4). None — если студент уже записан."""
    if get_enrollment(session, student_id, course_id) is not None:
        return None

    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment


def get_my_courses(session: Session, student_id: int) -> list[Course]:
    """Раздел «Мои курсы» — курсы, на которые записан студент."""
    stmt = (
        select(Course)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.student_id == student_id)
        .order_by(Enrollment.enrolled_at)
    )
    return list(session.execute(stmt).scalars().all())


def get_students_of_course(session: Session, course_id: int) -> list[User]:
    stmt = (
        select(User)
        .join(Enrollment, Enrollment.student_id == User.id)
        .where(Enrollment.course_id == course_id)
        .options(selectinload(User.role))
        .order_by(User.id)
    )
    return list(session.execute(stmt).scalars().all())


def get_student_ids_of_course(session: Session, course_id: int) -> list[int]:
    stmt = select(Enrollment.student_id).where(Enrollment.course_id == course_id)
    return list(session.execute(stmt).scalars().all())


def delete_enrollment(session: Session, enrollment_id: int) -> bool:
    enrollment = session.get(Enrollment, enrollment_id)
    if enrollment is None:
        return False
    session.delete(enrollment)
    session.commit()
    return True
