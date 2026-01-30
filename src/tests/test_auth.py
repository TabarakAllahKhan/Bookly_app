from src.auth.schemas import UserCreateModel
auth_prefix=f"/api/v1/auth"
auth_prefix = "/api/v1/auth"
def test_user_creation(test_session, test_user_service, test_client):
    signup_data={
        "username": "pathan",
        "email": "khan@gmail.com",
        "password": "orankh",
    }
    response=test_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data
    )
    user_data=UserCreateModel(**signup_data)
    assert test_user_service.user_exists_called_once()
    assert test_user_service.create_user_called_once_with(user_data,test_session)
    