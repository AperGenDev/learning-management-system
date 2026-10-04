"""
Заполняет базу тестовыми данными: роли, категории, пользователи
(преподаватели и студенты), курсы, модули и записи на курсы.

Запускать один раз на пустой базе:
    python seed_data.py
"""

from utils import fake_hash
from crud import (
    create_role, create_category, create_user,
    create_course, create_module, enroll_student,
)

def run():
    # --- роли (создаются ПЕРВЫМИ, иначе create_user упадёт) ---
    create_role("student", "Студент — проходит обучение")
    create_role("teacher", "Преподаватель — создаёт курсы")
    create_role("admin", "Администратор — управляет системой")
    print("Роли созданы: student, teacher, admin")

    # --- категории ---
    cat_python = create_category("Python", "Курсы по языку Python")
    cat_web = create_category("Веб-разработка", "Фронтенд и бэкенд разработка")
    print(f"Созданы категории: {cat_python}, {cat_web}")

    # --- пользователи ---
    teacher = create_user(
        full_name="Иван Преподавателев",
        email="teacher@example.com",
        password_hash=fake_hash("teacher123"),
        role_name="teacher",     # ← имя роли, а не строка role
    )
    student = create_user(
        full_name="Пётр Студентов",
        email="student@example.com",
        password_hash=fake_hash("student123"),
        role_name="student",
    )
    admin = create_user(
        full_name="Админ Админов",
        email="admin@example.com",
        password_hash=fake_hash("admin123"),
        role_name="admin",
    )
    print(f"Созданы пользователи: {teacher}, {student}, {admin}")

    # --- курс с модулями ---
    course = create_course(
        title="Основы Python",
        description="Курс для начинающих: синтаксис, типы данных, функции",
        author_id=teacher.id,
        category_id=cat_python.id,
        is_published=True,
    )
    create_module(course.id, "Введение", order_num=1, content="Установка Python, первая программа")
    create_module(course.id, "Переменные и типы данных", order_num=2, content="int, str, list, dict")
    create_module(course.id, "Функции", order_num=3, content="Определение и вызов функций")
    print(f"Создан курс с модулями: {course}")

    # --- запись студента на курс ---
    enrollment = enroll_student(student_id=student.id, course_id=course.id)
    print(f"Студент записан на курс: {enrollment}")

    print("\nТестовые данные успешно загружены.")


if __name__ == "__main__":
    run()