from database import SessionLocal
from models import Role, User, Category, Course, Module, Enrollment
from sqlalchemy import delete   
def clear_all():
    with SessionLocal() as session:
        session.execute(delete(Enrollment))
        session.execute(delete(Module))
        session.execute(delete(Course))
        session.execute(delete(User))
        session.execute(delete(Category))
        session.execute(delete(Role))
        session.commit()
    print("БД очищена.")

if __name__ == "__main__":
    clear_all()