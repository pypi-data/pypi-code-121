from typing import List

from fastapi import APIRouter, HTTPException, Depends
from minumtium.modules.posts import (PostNotFoundException,
                                     PostService,
                                     InvalidPageArgumentException,
                                     Post, NoPostsException)
from pydantic import BaseModel

from ..auth import authenticate
from ..deps import posts_service

posts_router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


@posts_router.get('/get/latest', response_model=Post)
async def get_latest_post(service: PostService = Depends(posts_service)):
    try:
        return service.get_latest_post()
    except NoPostsException as e:
        raise HTTPException(status_code=404, detail=str(e))


@posts_router.get('/get/{post_id}', response_model=Post)
async def get_posts(post_id: str, service: PostService = Depends(posts_service)):
    try:
        return service.get_post(post_id)
    except PostNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


class GetPostsResponse(BaseModel):
    posts: List[Post]


@posts_router.get('/summary', response_model=GetPostsResponse, response_model_exclude_none=True)
async def get_summary(service: PostService = Depends(posts_service)):
    return GetPostsResponse(posts=service.get_latest_posts_summary())


@posts_router.get('/page/{page}', response_model=GetPostsResponse)
async def get_posts(page: int, service: PostService = Depends(posts_service)):
    try:
        return GetPostsResponse(posts=service.get_posts_for_page(page))
    except InvalidPageArgumentException as e:
        raise HTTPException(status_code=422, detail=str(e))


class GetPagesResponse(BaseModel):
    page_count: int


@posts_router.get('/pages', response_model=GetPagesResponse)
async def get_posts(service: PostService = Depends(posts_service)):
    return GetPagesResponse(page_count=service.get_page_count())


class AddPostRequest(BaseModel):
    author: str
    title: str
    body: str


class AddPostResponse(BaseModel):
    id: str


@posts_router.post('/add', response_model=AddPostResponse, status_code=201, dependencies=[Depends(authenticate)])
async def add_post(post: AddPostRequest, service: PostService = Depends(posts_service)):
    try:
        post_id = service.add_post(**post.dict())
        return AddPostResponse(id=post_id)
    except InvalidPageArgumentException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
