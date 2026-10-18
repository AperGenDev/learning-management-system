from backend.database import SessionLocal
from backend.crud import (
    create_role, create_category, create_user,
    create_course, create_module, enroll_student,
)
from backend.security import hash_password

def run():
    with SessionLocal() as session:
        create_role(session, "student", "Студент — проходит обучение")
        create_role(session, "teacher", "Преподаватель — создаёт курсы")
        create_role(session, "admin", "Администратор — управляет системой")
        print("Роли созданы: student, teacher, admin")

        cat_python = create_category(session, "Python", "Курсы по языку Python")
        cat_web = create_category(session, "Веб-разработка", "Фронтенд и бэкенд разработка")
        print(f"Созданы категории: {cat_python}, {cat_web}")

        teacher = create_user(
            session,
            full_name="Иван Преподавателев",
            email="teacher@example.com",
            password_hash=hash_password("teacher123"),
            role_name="teacher",
        )
        student = create_user(
            session,
            full_name="Пётр Студентов",
            email="student@example.com",
            password_hash=hash_password("student123"),
            role_name="student",
        )
        admin = create_user(
            session,
            full_name="Админ Админов",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role_name="admin",
        )
        print(f"Созданы пользователи: {teacher}, {student}, {admin}")

        course = create_course(
            session,
            title="Основы Python",
            description="Курс для начинающих: синтаксис, типы данных, функции",
            author_id=teacher.id,
            category_id=cat_python.id,
            is_published=True,
        )
        create_module(session, course.id, "Введение", order_num=1, content="Установка Python, первая программа")
        create_module(session, course.id, "Переменные и типы данных", order_num=2, content="int, str, list, dict")
        create_module(session, course.id, "Функции", order_num=3, content="Определение и вызов функций")
        print(f"Создан курс с модулями: {course}")

        enrollment = enroll_student(session, student_id=student.id, course_id=course.id)
        print(f"Студент записан на курс: {enrollment}")

        print("\nТестовые данные успешно загружены.")


if __name__ == "__main__":
    run()