#!/usr/bin/env python

__version__ = '0.3.0'

import sys

if sys.version_info.major !=3 or sys.version_info.minor < 8:
    print('\033[41m', end='')
    print('=========================> ERROR <=============================')
    print('>       The minimum supported Python version is 3.8.          <')
    print('>          Please install it and then try again.              <')
    print('===============================================================\033[0m')
    exit(1)

import argparse
import datetime
import os
import random
import subprocess
from pathlib import Path
import json
from typing import List

from fastapi.responses import RedirectResponse
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

import uvicorn
from uvicorn.config import TRACE_LOG_LEVEL, LOGGING_CONFIG

from core import schemas
from core.config import Settings, get_settings
from core.logger import get_logger


root_folder = os.path.dirname(os.path.realpath(__file__))
settings = get_settings(_env_file=f'{root_folder}/.env')
settings.ROOT_FOLDER = root_folder
logger = get_logger()

def create_folder(folder):
    if not Path(folder).exists():
        os.mkdir(folder)

def add_cors_middleware(app: FastAPI, origins: List[str]):

    logger.debug('Origins', origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['GET', 'OPTIONS', 'GET', 'PUT', 'POST', 'DELETE'],
        allow_headers=["*"],
    )

def mount_folders(app: FastAPI, settings: Settings):
    scans_folder = f'{settings.SCANS_FOLDER}'
    app_folder = f'{settings.ROOT_FOLDER}/{settings.APP_FOLDER}'
    create_folder(scans_folder)
    create_folder(app_folder)

    app.mount(settings.SCANS_ADDRESS, StaticFiles(directory=scans_folder), name="scans")
    app.mount(settings.APP_ADDRESS, StaticFiles(directory=app_folder, html=True), name="root")


app = FastAPI()

@app.get('/')
def root_get():
    return RedirectResponse('/app')

@app.post('/scan/execute')
def scan_execute(
    req: schemas.ScanRequest
):
    params = [
        '--mode', req.mode,
        '-l', '0',
        '-t', '0',
        '-x', '211',
        '-y', '297',
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
    params.append(f'-o{settings.SCANS_FOLDER}/{filename}')
    
    p = subprocess.run(
        ["scanimage"] + params, 
        capture_output=True, 
        text=True, 
        universal_newlines=True, 
        encoding='utf-8', 
        errors='ignore'
    )
    
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



@app.post('/scan/update')
def endpoint_images_update_post(
    request: Request,
    file: UploadFile = File(...),
):
    target_folder = Path(settings.SCANS_FOLDER)
    if not os.path.isdir(target_folder):
        os.mkdir(target_folder)

    target_filepath = target_folder / file.filename
    with open(target_filepath, 'wb+') as file_object:
        filesize = file_object.write(file.file.read())

    return True


@app.get('/scans')
def endpoint_images_update_post():
    return list(filter(lambda x: Path(x).suffix in ['.jpg', '.jpeg', '.png', '.pdf'], os.listdir(settings.SCANS_FOLDER)))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Simple Web-based Interface for Scanner', 
        epilog='python swis.py --ip 192.168.1.105 --port 5520'
    )
    parser.add_argument('-i', '--ip', dest='ip', type=str, default='127.0.0.1', help='IP or hostname')
    parser.add_argument('-p', '--port', dest='port', type=str, default='5520',      help='port')
    parser.add_argument('-d', '--destination', dest='destination', type=str, default='scans', help='destination for scanned documents')
    args = parser.parse_args()

    if args.ip:
        settings.IP_ADDRESS = args.ip

    if args.port:
        settings.PORT = args.port

    if args.destination:
        settings.SCANS_FOLDER = args.destination

    LOGGING_CONFIG['formatters']['default']['fmt'] = '%(levelprefix)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s'
    LOGGING_CONFIG['formatters']['access']['fmt']  = '%(levelprefix)s %(asctime)s (%(client_addr)s) [%(name)s] %(message)s'
    for logger_ in LOGGING_CONFIG['loggers']:
        LOGGING_CONFIG['loggers'][logger_]['level'] = settings.LOG_LEVEL
    for formatter in LOGGING_CONFIG['formatters']:
        LOGGING_CONFIG['formatters'][formatter]['datefmt'] = '%Y-%m-%d %H:%M:%S'

    origins = [
        f'http://{settings.IP_ADDRESS}:{settings.PORT}',
        # The below entries can be removed (if not used on server)
        f'http://127.0.0.1:{settings.PORT}',
        f'http://localhost:{settings.PORT}',
        # The below can be removed (only for debug/dev purpose)
        f'http://127.0.0.1:8080',
        f'http://localhost:8080'
    ]

    add_cors_middleware(app, origins)
    mount_folders(app, settings)

    front_config = {
        'COMMENT': '!!!DO NOT EDIT MANUALLY!!!',
        'api_url' : settings.IP_ADDRESS,
        'api_port' : settings.PORT,
        'scans_url' : settings.SCANS_ADDRESS
    }

    with open(f'{settings.APP_FOLDER}/config.json', 'w') as f:
        json.dump(front_config, f)

    uvicorn.run(
        app, 
        host='0.0.0.0',
        port=int(settings.PORT),
        access_log=True,
        use_colors=True
    )
