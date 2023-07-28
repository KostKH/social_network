def test_users_login(active_client1, create_users):
    response = active_client1.post(
        '/api/v1/users/login',
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'},
        data=('grant_type=&username=User1&password=testpassword123'
              '&scope=&client_id=&client_secret='))
    data = response.json()
    keys = ['access_token', 'token_type']
    assert response.status_code == 200, 'Неверный код ответа'
    assert sorted(list(data.keys())) == keys, 'Неверные ключи в ответе'


def test_users_login_invalid_pass(active_client1, create_users):
    response = active_client1.post(
        '/api/v1/users/login',
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'},
        data=('grant_type=&username=User1&password=testpassword124'
              '&scope=&client_id=&client_secret='))
    assert response.status_code == 401, 'Неверный код ответа'
    data = response.json()
    assert data == {'detail': 'Введен неверный пароль.'}, (
        'Неверное тело ответа')


def test_users_get(test_client, create_users):
    response = test_client.get('/api/v1/users')
    assert response.status_code == 200, 'Неверный код ответа'
    data = response.json()
    user_num = len(create_users.values())

    assert len(data) == user_num, f'В ответе должно быть записей: {user_num}'
    for idx, item in enumerate(create_users.values()):
        user = item[0].__dict__.copy()
        user.pop('_sa_instance_state')
        user.pop('password')
        expected_keys = sorted(list(user.keys()))
        response_keys = sorted(list(data[idx].keys()))
        assert expected_keys == response_keys, (
            'ключи в ответе не такие, как ожидались')
        for key in expected_keys:
            assert user[key] == data[idx][key], (
                f'{user["username"]}, {key}: значение в ответе '
                'отличается от ожидаемого')


def test_users_signup_post_correct_data(test_client):
    new_user = {
        'username': 'User1001',
        'password': 'Testpass125',
        'name': 'Виктор1',
        'surname': 'Тестовый1001',
        'email': 'ccc@ddd.eee',
    }
    response = test_client.post('/api/v1/users/signup', json=new_user)
    data = response.json()
    assert response.status_code == 201, 'POST: Неверный код ответа'
    assert data.get('id') is not None, 'В ответе нет ключа `id`'
    new_user.pop('password')
    new_user['id'] = 1
    expected_items = sorted(list(data.items()))
    response_items = sorted(list(data.items()))
    assert expected_items == response_items, (
        'Полученный ответ не такой, как ожидалось.')


def test_users_signup_post_incorrect_data(test_client, create_users):
    new_user = {
        'username': 'User1001',
        'password': 'Testpass125',
        'name': 'Виктор1',
        'surname': 'Тестовый1001',
        'email': 'ccc@ddd.eee',
    }
    required_keys = ['username', 'password', 'name', 'surname', 'email']
    for key in required_keys:
        user = new_user.copy()
        user.pop(key)
        response = test_client.post(
            '/api/v1/users/signup',
            json=user)
        data = response.json()
        assert response.status_code == 422, 'Неверный код ответа'
        assert list(data.keys()) == ['detail'], 'Неверные ключи в ответе'
