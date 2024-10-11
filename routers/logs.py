from fastapi import APIRouter, status, Query, Path
from models.models import Log, Session, LogResponse
from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/",
            response_model=list[LogResponse],
            description="Получение всей истории запросов")
async def get_all_logs(page: int = Query(None, ge=1, description="Страница пагинации"),
                       limit: int = Query(None, ge=1, description="Количество записей на странице")):
    db = Session()
    if page and limit:
        logs_r = db.query(Log).offset((page-1) * limit).limit(limit)
    else:
        logs_r = db.query(Log).all()
    logs = []
    for log in logs_r:
        logs.append(LogResponse(log.user_id,
                                log.command,
                                log.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                log.answer))

    db.close()

    return logs


@router.get("/user/{user_id}",
            response_model=list[LogResponse],
            description="Получение исптории запросов отдельного пользователя")
async def get_logs(user_id: int = Path(description="ID пользователя"),
                   page: int = Query(None, ge=1, description="Страница пагинации"),
                   limit: int = Query(None, ge=1, description="Количество записей на странице")):
    db = Session()
    if page and limit:
        logs_r = db.query(Log).filter(Log.user_id==user_id).offset((page - 1) * limit).limit(limit)
    else:
        logs_r = db.query(Log).filter(Log.user_id==user_id).all()
    logs = []
    for log in logs_r:
        logs.append(LogResponse(log.user_id,
                                log.command,
                                log.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                log.answer))

    db.close()

    return logs
