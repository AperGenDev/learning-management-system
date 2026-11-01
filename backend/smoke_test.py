from backend.database import SessionLocal
from backend.services.auth_service import AuthService
from backend.schemas.user import UserCreate

db = SessionLocal()
svc = AuthService(db)
u = svc.register(UserCreate(full_name='T', email='t1@t.com', password='123456'))
print('registered:', u.id, u.email)
tok = svc.login('t1@t.com', '123456')
print('token:', tok.access_token[:40], '...')
db.close()