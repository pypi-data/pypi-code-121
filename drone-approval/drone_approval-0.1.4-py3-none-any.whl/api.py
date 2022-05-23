import uuid
import httpx
import secrets
import traceback
import logging
from datetime import datetime
from typing import List, Optional, Union

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import aiosmtplib
from fastapi import FastAPI, Response, Request, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from fastapi import APIRouter

from .config import settings, tortoise_orm_models
from . import schemas
from .models import ApprovalRequest, ApprovalGroup, Approval, ApprovalResult

logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()

known_users = {}

def authorized(authorization: str = Header(None)):
    if authorization != f'Bearer {settings.SECRET.get_secret_value()}':
        raise HTTPException(status_code=401, detail="You are not authorized")

async def send_notification_email(approval:Approval,approval_request:ApprovalRequest):
    msg = MIMEMultipart()
    # msg['From'] = 'martin.ortbauer@schindler.com'
    msg['To'] = approval.user_email
    msg['From'] = settings.SMTP_FROM_EMAIL
    # 'martin.ortbauer@schindler.com'
    msg['subject'] = f'Approval request for deployment {approval_request.name} from {approval_request.created_by}'

    text = f"""
    Your colleague {approval_request.created_by} would like to deploy {approval_request.repo} to {approval_request.name}.

    To approve or decline, go to the following link

    {settings.PUBLIC_URL}/approval/{approval.id}?token={approval.secret}

    and approve.
    """
    msg.attach(MIMEText(text))
    await aiosmtplib.send(msg,hostname=settings.SMTP_HOST,port=settings.SMTP_PORT)

async def approve_group(group,timestamp):
    group.approval_timestamp = timestamp
    logger.info("Saving approved group %s",group.id)
    await group.save()
    request = await ApprovalRequest.filter(id=group.request_id).first()
    await request.fetch_related('groups')
    if all((x.approval_timestamp is not None) for x in request.groups):
        await approve_request(request,timestamp)

async def approve_request(request,timestamp):
    request.approval_timestamp = timestamp
    await request.save()
    async with httpx.AsyncClient(base_url=settings.DRONE_SERVER,headers={'Authorization':f'Bearer {settings.DRONE_TOKEN}'}) as http_cl:
        resp = await http_cl.post(f'/api/repos/{request.repo}/builds/{request.build}')
        build_info = resp.json()
        approval_result = ApprovalResult(
            request_id=request.id,
            repo=request.repo,
            build=build_info['number'],
            created_at=datetime.now(),
            approved=True,
        )
        await approval_result.save()
    logger.info('Restarted build for %s with %s',request,build_info)

async def fetch_approval_group(group_id:uuid.UUID):
    res = await ApprovalGroup.filter(id=group_id).first()
    if res is not None:
        await res.fetch_related('users')
        group = schemas.ApprovalGroup(
            name=res.name,
            count=res.count,
            approval_timestamp=res.approval_timestamp,
            users=[schemas.Approval.from_orm(x) for x in res.users],
            id=res.id,
        )
        return group


async def fetch_approval_request(**filter_args) -> Optional[schemas.ApprovalRequest]:
    requests = await ApprovalRequest.filter(**filter_args)
    if requests:
        req = requests[0]
        await req.fetch_related('groups')
        groups = []
        for group in req.groups:
            await group.fetch_related('users')
            users = []
            for user_obj in group.users:
                users.append(schemas.ApprovalNoGroup(
                    id=user_obj.id,
                    user_email=user_obj.user_email,
                    approval_timestamp=user_obj.approval_timestamp,
                    declined_timestamp=user_obj.declined_timestamp,
                ))
            groups.append(schemas.ApprovalGroupNoRequest(
                name=group.name,
                count=group.count,
                users=users,
                id=group.id,
                approval_timestamp=group.approval_timestamp,
            ))
        return schemas.ApprovalRequest(
            repo=req.repo,
            name=req.name,
            created_at=req.created_at,
            created_by=req.created_by,
            build=req.build,
            stage=req.stage,
            step=req.step,
            groups=groups,
            id=req.id,
            approval_timestamp=req.approval_timestamp,
            declined_timestamp=req.declined_timestamp,
            build_href=f'{settings.DRONE_SERVER}/{req.repo}/{req.build}',
            author_avatar=known_users.get(req.created_by,{}).get('avatar')
        )

@router.post("/approval-requests")
async def create_new_approval(req:schemas.ApprovalRequestCreate, auth=Depends(authorized)):
    if not req.created_by:
        async with httpx.AsyncClient(base_url=settings.DRONE_SERVER,headers={'Authorization':f'Bearer {settings.DRONE_TOKEN}'}) as http_cl:
            resp = await http_cl.get(f'/api/repos/{req.repo}/builds/{req.build}')
            build_info = resp.json()
        if 'author_email' in build_info:
            req.created_by = build_info['author_email']
    approval_request =  ApprovalRequest(
        created_at=datetime.now(),
        **req.dict(exclude={'groups'}),
    )
    await approval_request.save()
    for group in req.groups:
        approval_group = ApprovalGroup(request_id=approval_request.id,**group.dict(exclude={'users'}))
        await approval_group.save()
        for user in group.users:
            ap = Approval(
                group_id=approval_group.id,
                user_email=user,
                secret=secrets.token_urlsafe(15),
            )
            await ap.save()
            await send_notification_email(ap,approval_request)

    res = await fetch_approval_request(id=approval_request.id)
    return res

@router.get("/approval-group/{group_id}")
async def get_approval_group(group_id:uuid.UUID):
    return await fetch_approval_group(group_id=group_id)

@router.get("/approval/{ap_id}")
async def get_approval(ap_id:uuid.UUID):
    return await fetch_approval(ap_id)

async def fetch_approval(ap_id:int):
    res = await Approval.filter(id=ap_id).first()
    if res is not None:
        await res.fetch_related('group')
        await res.group.fetch_related('request','users')
        await res.group.request.fetch_related('groups')
        approval_request = await fetch_approval_request(id=res.group.request.id)
        group = schemas.ApprovalGroupNoUserDetails(
            id=res.group.id,
            users=[x.user_email for x in res.group.users],
            name=res.group.name,
            count=res.group.count,
            request=approval_request,
            approval_timestamp=res.group.approval_timestamp,
        )
        ret = schemas.Approval(
            id=res.id,
            user_email=res.user_email,
            approval_timestamp=res.approval_timestamp,
            declined_timestamp=res.declined_timestamp,
            group=group,
        )
        return ret

@router.post("/approval/{ap_id}")
async def handle_approval(ap_id:uuid.UUID,token:str,decline:bool=False):
    logger.info('Got %s',decline)
    if decline:
        return await decline_approval(ap_id,token)
    else:
        return await approve_approval(ap_id,token)

async def approve_approval(ap_id:uuid.UUID,token:str):
    res = await Approval.filter(id=ap_id,approval_timestamp=None).first()
    if res is not None:
        if res.secret != token:
            logger.debug('Provided secret %s our token %s',token,res.secret)
            raise HTTPException(status_code=401, detail="Token not matching")
        now = datetime.now()
        res.approval_timestamp = now
        await res.save()
        group = await ApprovalGroup.filter(id=res.group_id,approval_timestamp=None).first()
        if group is not None:
            await group.fetch_related('users')
            approved = [x for x in group.users if x.approval_timestamp and x.declined_timestamp == None]
            if len(approved) >= group.count:
                await approve_group(group,timestamp=now)
            else:
                logger.info("not yet ready for approval")
        else:
            logger.info("no group found for %s",res.group_id)
        return await fetch_approval(res.id)
    else:
        logger.info("no pending approval found for %s",ap_id)

async def decline_approval(ap_id:uuid.UUID,token:str):
    res = await Approval.filter(id=ap_id).first()
    if res is not None:
        if res.secret != token:
            logger.debug('Provided secret %s our token %s',token,res.secret)
            raise HTTPException(status_code=401, detail="Token not matching")
        now = datetime.now()
        res.declined_timestamp = now
        await res.save()
        await res.fetch_related('group')
        ap_request = await ApprovalRequest.filter(id=res.group.request_id).first()
        ap_request.declined_timestamp = now
        await ap_request.save()
        return await fetch_approval(res.id)
    else:
        logger.info("no pending approval found for %s",ap_id)


@router.get("/approval-requests")
async def list_pending_approvals():
    requests = await ApprovalRequest.filter(approval_timestamp=None,declined_timestamp=None)
    results = []
    for req in requests:
        results.append(await fetch_approval_request(id=req.id))
    return results

@router.get("/approval-result",response_model=schemas.ApprovalResult)
async def get_approval_result(repo:str,build:int,response:Response):
    res = await ApprovalResult.filter(build=build,repo=repo)
    if res:
        item= res[0]
        request = await fetch_approval_request(id=item.request_id)
        return schemas.ApprovalResult(
            build=build,
            request=request,
            created_at=item.created_at,
            approved=item.approved,
            )
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return None


@router.get("/approval-requests/search",response_model=schemas.ApprovalRequest)
async def get_approval_request(response: Response,id:Optional[uuid.UUID]=None,build:Optional[int]=None):
    if id:
        res = await fetch_approval_request(id=id)
    elif build:
        res = await fetch_approval_request(build=build)
    if res is None:
        response.status_code = status.HTTP_204_NO_CONTENT
    return res


@router.get("/approval-group/{group_id}")
async def get_approval_group(group_id:uuid.UUID):
    return await fetch_approval_group(group_id=group_id)

@router.get("/approval/{ap_id}")
async def get_approval(ap_id:uuid.UUID):
    return await fetch_approval(ap_id)

@app.on_event("startup")
async def startup_event():
    async with httpx.AsyncClient(base_url=settings.DRONE_SERVER,headers={'Authorization':f'Bearer {settings.DRONE_TOKEN}'}) as http_cl:
        try:
            resp = await http_cl.get(f'/api/users',timeout=1)
            for item in resp.json():
                known_users[item['email']] = item
                logger.debug('Adding user %s',item)
        except Exception as exc:
            logger.exception('Failed getting the users')

register_tortoise(
    app,
    db_url=settings.DB_DSN,
    modules={"models": ["drone_approval.models"]},
    generate_schemas=False,
    add_exception_handlers=True,
)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

if settings.DEBUG:
    @app.exception_handler(Exception)
    async def debug_exception_handler(request: Request, exc: Exception):
        return Response(
            content="".join(
                traceback.format_exception(
                    etype=type(exc), value=exc, tb=exc.__traceback__
                )
            )
        )
else:
    @app.exception_handler(Exception)
    async def logging_exception_handler(request: Request, exc: Exception):
        logger.exception(f'Handling {request} failed with {exc}')


app.include_router(router, prefix=settings.API_V1_STR)
