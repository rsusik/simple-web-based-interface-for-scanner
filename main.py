import datetime
import os
import random
from typing import Any, Dict, List, Optional

from pathlib import Path
import unicodedata
import uuid

from fastapi import FastAPI, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_200_OK, HTTP_402_PAYMENT_REQUIRED, HTTP_406_NOT_ACCEPTABLE

from core import schemas
from core.config import get_settings
from core.logger import get_logger

settings = get_settings()
logger = get_logger()

origins = [
    settings.DOMAIN_URL_API,
    settings.DOMAIN_URL_CLIENT,
    'http://localhost:8080'
]

logger.debug('Origins', origins)

app = FastAPI(
    # openapi_url=None,
    # docs_url=None,
    # redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'OPTIONS', 'GET', 'PUT', 'POST', 'DELETE'],
    allow_headers=["*"],
)

# app.mount("/scans", StaticFiles(directory=settings.SCANS_DESTINATION), name="scans")
app.mount("/scans", StaticFiles(directory=settings.SCANS_DESTINATION), name="scans")


@app.post('/scan/execute')
def create_db(
    req: schemas.ScanRequest
):
    import subprocess

    params = [
        '--mode', req.mode,
        #'-l', req.margin_left,
        #'-t', req.margin_top,
        #'-x', req.width,
        #'-y', req.height,
        '-l', 0,
        '-t', 0,
        '-x', 211,
        '-y', 297,
        f'--resolution={req.resolution}',
        f'--format={req.format}',
        f'--buffer-size={settings.BUFFER_SIZE}'
    ]

    map_format_ext = {
        'png': 'png',
        'jpeg': 'jpg',
        'pdf': 'pdf'
    }
    file_ext = map_format_ext[req.format]

    filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '_' + str(random.randint(10, 99)) + f'.{file_ext}'
    if req.filename:
        filename = req.filename
    params.append(f'-o{settings.SCANS_DESTINATION}/{filename}')
    

    p = subprocess.run(["scanimage"] + params, capture_output=True, text=True, universal_newlines=True, encoding='utf-8', errors='ignore')
    
    out = p.stdout
    err = p.stderr
    code = p.returncode
    logger.info(out + err)
    logger.info(code)
    
    return schemas.ScanResult(
        code = code,
        detail = out if code==0 else err,
        filename = filename
    )



@app.post('/images/update')
def endpoint_images_uploadimage_post(
    request: Request,
    file: UploadFile = File(...),
):
    if 'content-length' not in request.headers or int(request.headers['content-length']) > settings.FILE_SIZE_LIMIT:
        logger.error(f'{request.client.host} | {file.filename} | Content length is not provided or file is too large')
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='Content length is not provided or file is too large'
        )
    
    # Save image
    target_folder = Path(settings.SCANS_DESTINATION)
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    target_filepath = target_folder / file.filename
    with open(target_filepath, 'wb+') as file_object:
        filesize = file_object.write(file.file.read())

    return True





if __name__ == '__main__':
    import uvicorn
    from uvicorn.config import TRACE_LOG_LEVEL, LOGGING_CONFIG
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(levelprefix)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"]  = "%(levelprefix)s %(asctime)s (%(client_addr)s) [%(name)s] %(message)s"
    for logger_ in LOGGING_CONFIG["loggers"]:
        LOGGING_CONFIG["loggers"][logger_]['level'] = settings.LOG_LEVEL
    for formatter in LOGGING_CONFIG["formatters"]:
        LOGGING_CONFIG["formatters"][formatter]['datefmt'] = '%Y-%m-%d %H:%M:%S'

    uvicorn.run(
        app, 
        host=settings.API_HOSTNAME, 
        port=int(settings.API_PORT),
        access_log=True,
        use_colors=True
    )

# uvicorn main:app --host localhost --port 36453 --ssl-keyfile localhost.key --ssl-certfile localhost.crt