from datetime import datetime

from backend import crud
from backend.database import SessionLocal
from backend.security import hash_password, verify_password

SUFFIX = datetime.now().strftime("%H%M%S")


def scenario_registration(session):
    print("\n--- Сценарий 1: Регистрация ---")
    email = f"new_user_{SUFFIX}@example.com"
    if crud.get_user_by_email(session, email):
        print("Пользователь с таким email уже есть")
        return None
    user = crud.create_user(session, full_name="Новый Студент", email=email,
                            password_hash=hash_password("mypassword"), role_name="student")
    print(f"Зарегистрирован: {user}, роль: {user.role.name}")
    return user


def scenario_login(session, email: str, password: str):
    print("\n--- Сценарий 2: Авторизация ---")
    user = crud.get_user_by_email(session, email)
    if user is None or not verify_password(password, user.password_hash):
        print("Неверный email или пароль")
        return None
    print(f"Авторизация успешна: {user}, роль: {user.role.name}")
    return user


def scenario_catalog(session):
    print("\n--- Сценарий 3: Просмотр каталога ---")
    for course in crud.get_courses_catalog(session):
        print(f"  {course}")
    category = crud.get_category_by_name(session, "Python")
    if category:
        print(f"Фильтр по категории '{category.name}': {crud.get_courses_catalog(session, category.id)}")


def scenario_create_course(session, teacher):
    print("\n--- Сценарий 6: Создание курса преподавателем ---")
    category = crud.get_category_by_name(session, "Базы данных")
    course = crud.create_course(session, title=f"PostgreSQL {SUFFIX}",
                                description="Основы PostgreSQL", author_id=teacher.id,
                                category_id=category.id if category else None, is_published=True)
    module1 = crud.create_module(session, course.id, "Введение в PostgreSQL", order_num=1, content="Что такое СУБД")
    module2 = crud.create_module(session, course.id, "Индексы", order_num=2, content="B-tree и когда он нужен")
    print(f"Создан курс: {course}\nДобавлены модули: {module1}, {module2}")

    crud.update_course(session, course.id, description="Основы PostgreSQL (обновлено)")
    print(f"Курс отредактирован: {crud.get_course_by_id(session, course.id).description}")
    return course


def scenario_enrollment(session, student, course):
    print("\n--- Сценарий 4: Запись на курс ---")
    enrollment = crud.enroll_student(session, student.id, course.id)
    print(f"Запись создана: {enrollment}")
    again = crud.enroll_student(session, student.id, course.id)
    print(f"Повторная запись: {'отклонена (уже записан)' if again is None else again}")
    print(f"«Мои курсы» студента: {crud.get_my_courses(session, student.id)}")


def scenario_course_progress(session, course):
    print("\n--- Сценарий 5: Прохождение курса ---")
    for module in crud.get_modules_by_course(session, course.id):
        print(f"  {module.order_num}. {module.title} — {module.content}")


def scenario_cleanup(session, course, user):
    print("\n--- Удаление (D в CRUD) ---")
    print(f"Удалён курс {course.id}: {crud.delete_course(session, course.id)} (модули и записи удалены каскадно)")
    if user:
        print(f"Удалён пользователь {user.id}: {crud.delete_user(session, user.id)}")


def main() -> None:
    with SessionLocal() as session:
        if crud.get_role_by_name(session, "student") is None:
            print("Сначала загрузите тестовые данные: python -m backend.seed_data")
            return

        new_user = scenario_registration(session)
        student = scenario_login(session, "student@example.com", "student123")
        scenario_login(session, "student@example.com", "wrong-password")
        scenario_catalog(session)

        teacher = crud.get_user_by_email(session, "teacher@example.com")
        course = scenario_create_course(session, teacher)
        if student:
            scenario_enrollment(session, student, course)
        scenario_course_progress(session, course)
        print(f"\nСтуденты курса '{course.title}': {crud.get_students_of_course(session, course.id)}")
        scenario_cleanup(session, course, new_user)


if __name__ == "__main__":
    main()
