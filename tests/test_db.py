from sqlmodel import select

from src.models.user import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as (create_time, update_time):
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
        'created_at': create_time,
        'updated_at': create_time,
    }


def test_update_user(session, mock_db_time):
    with mock_db_time(model=User) as (create_time, update_time):
        # criando user
        new_user = User(
            username='Lex', password='s&cret', email='lex@mail.com'
        )
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'Lex'))

        # atualizando user
        user_updates = {
            'username': 'Lexus',
            'password': 'NewP@ss',
            'email': 'lexus@mail.com',
        }

        # cada attr do user recebe como novo valor o que está no
        # dict user_updates
        for attr, value in user_updates.items():
            setattr(user, attr, value)

        session.add(user)
        session.commit()

        # assert
        updated_user = session.scalar(
            select(User).where(User.username == 'Lexus')
        )

        assert updated_user.dict() == {
            'id': 1,
            'username': 'Lexus',
            'password': 'NewP@ss',
            'email': 'lexus@mail.com',
            'created_at': create_time,
            'updated_at': update_time,
        }
