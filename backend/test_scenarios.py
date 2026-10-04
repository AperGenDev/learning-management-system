"""
Демонстрационный скрипт: прогоняет основные сценарии использования из ЛР0

Запускать после create_tables.py и seed_data.py:
    python test_scenarios.py
"""

from utils import fake_hash
import crud

def scenario_registration():
    print("\n--- Сценарий 1: Регистрация ---")
    user = crud.create_user(
        full_name="Данил Богданов",
        email="new_mail@example.com",
        password_hash=fake_hash("mypassword"),
        role_name="student",
    )
    print(f"Зарегистрирован новый пользователь: {user}")
    return user


def scenario_login(email: str, password: str):
    print("\n--- Сценарий 2: Авторизация ---")
    user = crud.get_user_by_email(email)
    if user is None:
        print("Пользователь не найден")
        return None
    if user.password_hash == fake_hash(password):
        print(f"Авторизация успешна: {user}, роль: {user.role}")
        return user
    print("Неверный пароль")
    return None


def scenario_catalog():
    print("\n--- Сценарий 3: Просмотр каталога курсов ---")
    all_courses = crud.get_courses_catalog()
    print(f"Все опубликованные курсы: {all_courses}")

    categories = crud.get_all_categories()
    if categories:
        first_category = categories[0]
        filtered = crud.get_courses_catalog(category_id=first_category.id)
        print(f"Курсы в категории '{first_category.name}': {filtered}")


def scenario_enrollment(student_id: int, course_id: int):
    print("\n--- Сценарий 4: Запись на курс ---")
    result = crud.enroll_student(student_id=student_id, course_id=course_id)
    if result is None:
        print("Студент уже был записан на этот курс ранее — новая запись не создана")
    else:
        print(f"Студент записан на курс: {result}")

    my_courses = crud.get_my_courses(student_id)
    print(f"Раздел «Мои курсы» студента: {my_courses}")


def scenario_course_progress(course_id: int):
    print("\n--- Сценарий 5: Прохождение курса ---")
    modules = crud.get_modules_by_course(course_id)
    print(f"Структура курса (модули по порядку):")
    for module in modules:
        print(f"  {module.order_num}. {module.title} — {module.content}")


def scenario_create_course(teacher_id: int, category_id: int):
    print("\n--- Сценарий 6: Создание курса преподавателем ---")
    course = crud.create_course(
        title="Postgress SQL",
        description="Основы реляционных баз данных и языка SQL Postgress",
        author_id=teacher_id,
        category_id=category_id,
        is_published=True,
    )
    module = crud.create_module(course.id, "Введение в PSQL", order_num=1, content="Что такое SQL")
    print(f"Создан курс: {course}")
    print(f"Добавлен модуль: {module}")
    return course


def main():
    scenario_registration()

    student = scenario_login("student@example.com", "student123")

    scenario_catalog()

    teacher = crud.get_user_by_email("teacher@example.com")
    categories = crud.get_all_categories()
    new_course = scenario_create_course(teacher.id, categories[0].id)

    if student is not None:
        scenario_enrollment(student.id, new_course.id)
        scenario_course_progress(new_course.id)

    students_of_course = crud.get_students_of_course(new_course.id)
    print(f"\nСтуденты, записанные на курс '{new_course.title}': {students_of_course}")


if __name__ == "__main__":
    main()
