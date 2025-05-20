from sqlmodel import select

from src.models.user import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Lex', password='s&cret', email='lex@mail.com'
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'Lex'))

    assert user.dict() == {
        'id': 1,
        'username': 'Lex',
        'password': 's&cret',
        'email': 'lex@mail.com',
        'created_at': time,
        'updated_at': time,
    }
