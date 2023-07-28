def test_like_post_correct_data(active_client3, posts_likes_in_db):
    response = active_client3.post('/api/v1/like/2')
    data = response.json()
    assert response.status_code == 201, 'Неверный код ответа'

    expected_keys = sorted(['post_id', 'liker_id'])
    response_keys = sorted(list(data.keys()))
    assert expected_keys == response_keys, (
        'ключи в ответе не такие, как ожидались')

    assert data.get('liker_id') == 3, 'Некорректный id пользователя'
    assert data.get('post_id') == 2, 'Некорректный id поста'
    num_likes = active_client3.get('/api/v1/posts/2').json()['like_count']
    assert num_likes == 2, 'неверное кол-во лайков в посте'


def test_like_delete(active_client3, posts_likes_in_db):
    response = active_client3.delete('/api/v1/like/1')
    data = response.json()
    assert response.status_code == 404, 'Неверный код ответа'
    assert list(data.keys()) == ['detail'], 'Неверный ключ в ответе'
    num_likes = active_client3.get('/api/v1/posts/1').json()['like_count']
    assert num_likes == 1, 'неверное кол-во лайков в посте'


def test_like_post_double_not_allowed(active_client3, posts_likes_in_db):
    response = active_client3.post('/api/v1/like/1')
    data = response.json()
    assert response.status_code == 403, 'Неверный код ответа'
    assert list(data.keys()) == ['detail'], 'Неверный ключ в ответе'
    num_likes = active_client3.get('/api/v1/posts/1').json()['like_count']
    assert num_likes == 0, 'неверное кол-во лайков в посте'


def test_like_post_del_unauthorized_no_access(test_client, posts_in_db):
    methods = ['post', 'delete']
    for method in methods:
        func = getattr(test_client, method)
        response = func('/api/v1/like/1')
        data = response.json()
        assert response.status_code == 403, 'Неверный код ответа'
        assert list(data.keys()) == ['detail'], 'Неверный ключ в ответе'
