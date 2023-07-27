from business_layer import schemas
from db_layer import db_engine as db
from db_layer.crud import like_crud, post_crud


async def change_like_in_post(post_id: int, session: db.AsyncSession) -> None:
    post = await post_crud.get(obj_id=post_id, session=session)
    like_count = await like_crud.count_likes(
        post_id=post_id,
        session=session,)
    update_likes_in_post = schemas.PostLikeUpdate(
        id=post_id,
        like_count=like_count,)
    await post_crud.update(
        obj=post,
        update_data=update_likes_in_post,
        session=session,)
