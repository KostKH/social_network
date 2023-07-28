def test_posts_get(test_client, posts_in_db):
    response = test_client.get('/api/v1/posts')
    assert response.status_code == 200, 'Неверный код ответа'
    data = response.json()
    post_num = len(posts_in_db[0])

    assert len(data) == post_num, f'В ответе должно быть записей: {post_num}'
    for idx, item in enumerate(posts_in_db[0]):
        post = item.copy()
        post.pop('_sa_instance_state')
        expected_keys = sorted(list(post.keys()))
        response_keys = sorted(list(data[idx].keys()))
        assert expected_keys == response_keys, (
            'ключи в ответе не такие, как ожидались')
        for key in post.keys():
            assert post[key] == data[idx][key], (
                f'Пост {post["id"]}, {key}: значение в ответе '
                'отличается от ожидаемого')


def test_posts_post_correct_data(active_client1, create_users):
    new_post = {'text': 'Вот такой пост. не очень длинный'}
    response = active_client1.post('/api/v1/posts', json=new_post)
    data = response.json()
    assert response.status_code == 201, 'Неверный код ответа'

    keys_to_be = ['text', 'author_id', 'update_timestamp',
                  'id', 'create_timestamp', 'like_count']
    expected_keys = sorted(keys_to_be)
    response_keys = sorted(list(data.keys()))
    assert expected_keys == response_keys, (
        'ключи в ответе не такие, как ожидались')

    assert data.get('author_id') == 1, 'Некорректный id автора'
    assert data.get('text') == new_post['text'], 'Некорректный текст поста'
    assert data.get('create_timestamp') > 0, 'Дата создания д.быть больше 0'
    assert data.get('update_timestamp') is None, 'Дата изменения д.быть None'
    assert data.get('like_count') == 0, 'Кол-во лайков д.быть 0'


def test_posts_post_unathorized_no_access(test_client, create_users):
    new_post = {'text': 'Вот такой пост. не очень длинный'}
    response = test_client.post('/api/v1/posts', json=new_post)
    data = response.json()
    assert response.status_code == 403, 'Неверный код ответа'
    assert list(data.keys()) == ['detail'], (
        'GET:Неверный ключ в ответе')


def test_posts_post_incorrect_data(active_client1, create_users):
    incorrect_posts = (
        {'textttt': 'Вот такой пост. не очень длинный'},
        {'text': 111},
        {}
    )
    for new_post in incorrect_posts:
        response = active_client1.post('/api/v1/posts', json=new_post)
        data = response.json()
        assert response.status_code == 422, 'Неверный код ответа'
        assert list(data.keys()) == ['detail'], (
            'POST:Неверный ключ в ответе')


def test_posts_id_get(test_client, posts_in_db):
    response = test_client.get('/api/v1/posts/1')
    assert response.status_code == 200, 'Неверный код ответа'
    data = response.json()

    post = posts_in_db[0][0].copy()
    post.pop('_sa_instance_state')
    expected_keys = sorted(list(post.keys()))
    response_keys = sorted(list(data.keys()))
    assert expected_keys == response_keys, (
        'ключи в ответе не такие, как ожидались')
    for key in post.keys():
        assert post[key] == data[key], (
            f'Пост {post["id"]}, {key}: значение в ответе '
            'отличается от ожидаемого')


def test_posts_id_patch_correct_data(active_client1, posts_in_db):
    updated_post = {'text': 'Измененный текст'}
    response = active_client1.patch('/api/v1/posts/1', json=updated_post)
    data = response.json()
    assert response.status_code == 200, 'Неверный код ответа'

    keys_to_be = ['text', 'author_id', 'update_timestamp',
                  'id', 'create_timestamp', 'like_count']
    expected_keys = sorted(keys_to_be)
    response_keys = sorted(list(data.keys()))
    assert expected_keys == response_keys, (
        'ключи в ответе не такие, как ожидались')

    assert data.get('author_id') == 1, 'Некорректный id автора'
    assert data.get('text') == updated_post['text'], 'Некорректный текст'
    assert data.get('create_timestamp') > 0, 'Дата создания д.быть больше 0'
    assert data.get('update_timestamp') > 0, 'Дата изменения д.быть больше 0'
    assert data.get('like_count') == 0, 'Кол-во лайков д.быть 0'


def test_posts_id_patch_unauthorized_no_access(active_client2, posts_in_db):
    updated_post = {'text': 'Измененный текст'}
    response = active_client2.patch('/api/v1/posts/1', json=updated_post)
    data = response.json()
    assert response.status_code == 403, 'Неверный код ответа'
    assert list(data.keys()) == ['detail'], 'Неверный ключ в ответе'


def test_posts_id_patch_incorrect_data(active_client1, posts_in_db):
    incorrect_posts = (
        {'textttt': 'Вот такой пост. не очень длинный'},
        {'text': 111},
        {}
    )
    for upd_post in incorrect_posts:
        response = active_client1.patch('/api/v1/posts/1', json=upd_post)
        data = response.json()
        assert response.status_code == 422, 'Неверный код ответа'
        assert list(data.keys()) == ['detail'], (
            'POST:Неверный ключ в ответе')


def test_posts_id_delete(active_client1, posts_likes_in_db):
    response = active_client1.delete('/api/v1/posts/1')
    assert response.status_code == 404, 'DELETE: Неверный код ответа'
    after_delete_resp = active_client1.get('/api/v1/posts/1')
    assert after_delete_resp.status_code == 404, 'GET: Неверный код ответа'


def test_posts_id_delete_unauthorized_no_access(
    active_client2,
    posts_likes_in_db
):
    response = active_client2.delete('/api/v1/posts/1')
    data = response.json()
    assert response.status_code == 403, 'Неверный код ответа'
    assert list(data.keys()) == ['detail'], 'Неверный ключ в ответе'
