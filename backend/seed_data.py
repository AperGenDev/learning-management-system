from backend.crud import (
    create_category, create_course, create_module, create_role, create_user,
    enroll_student, get_role_by_name,
)
from backend.database import SessionLocal
from backend.security import hash_password


def run() -> None:
    with SessionLocal() as session:
        if get_role_by_name(session, "student") is not None:
            print("Тестовые данные уже загружены — пропускаю.")
            return

        create_role(session, "student", "Студент — проходит обучение")
        create_role(session, "teacher", "Преподаватель — создаёт курсы")
        create_role(session, "admin", "Администратор — управляет системой")
        print("Роли созданы: student, teacher, admin")

        cat_python = create_category(session, "Python", "Курсы по языку Python")
        cat_web = create_category(session, "Веб-разработка", "Фронтенд и бэкенд разработка")
        cat_db = create_category(session, "Базы данных", "SQL и проектирование БД")
        print("Созданы категории: Python, Веб-разработка, Базы данных")

        teacher = create_user(session, "Иван Преподавателев", "teacher@example.com",
                              hash_password("teacher123"), "teacher")
        student = create_user(session, "Пётр Студентов", "student@example.com",
                              hash_password("student123"), "student")
        student2 = create_user(session, "Анна Учащаяся", "student2@example.com",
                               hash_password("student123"), "student")
        create_user(session, "Админ Админов", "admin@example.com",
                    hash_password("admin123"), "admin")
        print("Созданы пользователи: teacher, student, student2, admin")

        courses = {}
        for title, description, category in [
            ("Основы Python", "Синтаксис, типы данных, функции", cat_python),
            ("Продвинутый Python", "Генераторы, декораторы, асинхронность", cat_python),
            ("FastAPI с нуля", "Разработка REST API на Python", cat_web),
            ("HTML и CSS", "Вёрстка веб-страниц", cat_web),
            ("SQL для начинающих", "Запросы SELECT, JOIN, GROUP BY", cat_db),
        ]:
            courses[title] = create_course(session, title=title, description=description,
                                           author_id=teacher.id, category_id=category.id,
                                           is_published=True)
        create_course(session, title="Черновик: Docker", description="Курс ещё не опубликован",
                      author_id=teacher.id, category_id=cat_web.id, is_published=False)
        print(f"Создано курсов: {len(courses) + 1} (один — неопубликованный черновик)")

        base = courses["Основы Python"]
        create_module(session, base.id, "Введение", order_num=1, content="Установка Python, первая программа")
        create_module(session, base.id, "Переменные и типы данных", order_num=2, content="int, str, list, dict")
        create_module(session, base.id, "Функции", order_num=3, content="Определение и вызов функций")
        create_module(session, courses["FastAPI с нуля"].id, "Первое приложение", order_num=1,
                      content="Установка FastAPI и uvicorn")
        print("Созданы модули курсов")

        enroll_student(session, student.id, base.id)
        enroll_student(session, student2.id, base.id)
        enroll_student(session, student2.id, courses["FastAPI с нуля"].id)
        enroll_student(session, student2.id, courses["SQL для начинающих"].id)
        print("Студенты записаны на курсы")

        print("\nТестовые данные успешно загружены.")
        print("Логины: student@example.com / student123, teacher@example.com / teacher123, "
              "admin@example.com / admin123")


if __name__ == "__main__":
    run()
