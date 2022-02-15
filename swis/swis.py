#!/usr/bin/env python3

__version__ = '0.3.13'

import sys

if sys.version_info[0] !=3 or sys.version_info.minor < 8:
    print('\033[41m=========================> ERROR <=============================\033[0m')
    print('\033[41m>       The minimum supported Python version is 3.8.          <\033[0m')
    print('\033[41m>          Please install it and then try again.              <\033[0m')
    print('\033[41m===============================================================\033[0m')
    sys.exit(1)

import getpass
import errno
import pwd
import grp
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

from swis.core import schemas
from swis.core.config import Settings, get_settings
from swis.core.logger import get_logger


root_folder = os.path.dirname(os.path.realpath(__file__))
settings = get_settings(_env_file=f'{root_folder}/assets/defaults.env')
settings.ROOT_FOLDER = root_folder
logger = get_logger()

def restricted(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IOError as e:
            if (e.errno == errno.EPERM or e.errno == errno.EACCES):
                logger.exception('\033[41mPermission denied\033[0m')
                sys.exit('\033[41mPermission denied\033[0m')
            raise e
    return inner

@restricted
def create_folder(folder, user=None, group=None):
    if not Path(folder).exists():
        os.mkdir(folder)
        if user is not None and group is not None:
            os.chown(
                folder, 
                pwd.getpwnam(user).pw_uid, 
                grp.getgrnam(group).gr_gid
            )

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
    app_folder = f'{settings.APP_FOLDER}'
    create_folder(scans_folder, settings.USER, settings.GROUP)
    create_folder(app_folder)

    app.mount(settings.SCANS_ADDRESS, StaticFiles(directory=scans_folder), name="scans")
    app.mount(settings.APP_ADDRESS, StaticFiles(directory=app_folder, html=True), name="root")

@restricted
def read_file(path:str) -> str:
    with open(path, 'rt') as f:
        return f.read()

@restricted
def write_file(path:str, content:str) -> str:
    with open(path, 'wt') as f:
        return f.write(content)

def replace(d:dict, t:str) -> str:
    for k, v in d.items():
        t = t.replace(f'{{{{{k}}}}}', v)
    return t

@restricted
def _run_pocess(params:list) -> schemas.ProcessResult:
    logger.info('Executing: ' + ' '.join(params))
    p = subprocess.run(
        params, 
        capture_output=True, 
        text=True, 
        universal_newlines=True, 
        encoding='utf-8', 
        errors='ignore'
    )
    return schemas.ProcessResult(
        stdout = p.stdout,
        stderr = p.stderr,
        returncode = p.returncode
    )

def run_pocess(cmd:str, params:list) -> schemas.ProcessResult:
    return _run_pocess([cmd] + params)

def run_sudo_pocess(cmd:str, params:list) -> schemas.ProcessResult:
    return _run_pocess(['sudo', cmd] + params)

def service_install(
    settings:Settings,
    #python_path:str='/usr/bin/python3',
    user:str='root',
    group:str='root',
):
    serv_tpl = read_file(f'{settings.ROOT_FOLDER}/assets/swis.service')
    p = {
        '-i': settings.IP_ADDRESS,
        '-p': settings.PORT,
        '-d': settings.SCANS_FOLDER,
        '-u': settings.USER,
        '-g': settings.GROUP,
    }
    params = ' '.join([f'{k} "{v}"' for k, v in p.items()])
    serv_tpl = replace({
        #'PYTHON_PATH': python_path,
        'USER': user,
        'GROUP': group,
        'WD': settings.ROOT_FOLDER,
        'PARAMS': params,
    }, serv_tpl)

    write_file('/tmp/.swis.service', serv_tpl)
    if run_pocess('cp', ['/tmp/.swis.service', '/etc/systemd/system/swis.service']).returncode != 0:
        sys.exit("You need root permissions")
    if run_pocess('systemctl', ['daemon-reload']).returncode != 0:
        sys.exit("You need root permissions")
    if run_pocess('systemctl', ['enable', 'swis']).returncode != 0:
        sys.exit("You need root permissions")
    if run_pocess('systemctl', ['start', 'swis']).returncode != 0:
        sys.exit("You need root permissions")
    return True


def service_uninstall(
    settings:Settings,
):
    out = run_pocess('rm', ['/etc/systemd/system/swis.service'])
    if out.returncode != 0:
        sys.exit(out.stderr)
    if out.stdout: print(out.stdout)
    return out


def service_start(
    settings:Settings,
):
    out = run_pocess('systemctl', ['start', 'swis'])
    if out.returncode != 0:
        sys.exit(out.stderr)
    if out.stdout: print(out.stdout)
    return out


def service_stop(
    settings:Settings,
):
    out = run_pocess('systemctl', ['stop', 'swis'])
    if out.returncode != 0:
        sys.exit(out.stderr)
    if out.stdout: print(out.stdout)
    return out

def service_status(
    settings:Settings,
):
    out = run_pocess('systemctl', ['status', 'swis'])
    if out.returncode != 0:
        sys.exit(out.stderr or out.stdout)
    if out.stdout: print(out.stdout)
    return out
    
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
    create_folder(settings.SCANS_FOLDER, settings.USER,settings.GROUP)
    
    p = run_pocess('scanimage', params)
    
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
    create_folder(target_folder, settings.USER,settings.GROUP)

    target_filepath = target_folder / file.filename
    with open(target_filepath, 'wb+') as file_object:
        filesize = file_object.write(file.file.read())
    if settings.USER is not None and settings.GROUP is not None:
        os.chown(
            target_filepath, 
            pwd.getpwnam(settings.USER).pw_uid, 
            grp.getgrnam(settings.GROUP).gr_gid
        )

    return True


@app.get('/scans')
def endpoint_images_update_post():
    return list(filter(lambda x: Path(x).suffix in ['.jpg', '.jpeg', '.png', '.pdf'], os.listdir(settings.SCANS_FOLDER)))

def write_conf(settings:Settings):
    front_config = {
        'COMMENT': '!!!DO NOT EDIT MANUALLY!!!',
        'api_url' : settings.IP_ADDRESS,
        'api_port' : settings.PORT,
        'scans_url' : settings.SCANS_ADDRESS
    }

    with open(f'{settings.APP_FOLDER}/config.json', 'w') as f:
        json.dump(front_config, f)

def main():
    parser = argparse.ArgumentParser(
        description='Simple Web-based Interface for Scanner', 
        epilog='swis --ip 192.168.1.105 --port 5520'
    )
    parser.add_argument('-v', '--version', dest='version', action='version', version=f'Version: {__version__}')
    parser.add_argument('-i', '--ip', dest='ip', type=str, default='127.0.0.1', help='IP or hostname')
    parser.add_argument('-p', '--port', dest='port', type=str, default='5520',      help='port')
    parser.add_argument('-d', '--destination', dest='destination', type=str, default='scans', help='destination for scanned documents')
    parser.add_argument('-u', '--user', dest='user', type=str, default=None, help='user (default: current)')
    parser.add_argument('-g', '--group', dest='group', type=str, default=None, help='group (default: current)')
    parser.add_argument('--nocfg', default=False, action=argparse.BooleanOptionalAction, help='Do not replace front config (for dev purposes)')

    subparsers = parser.add_subparsers(help='Option', dest='option', required=False)
    parser_service_subparsers = subparsers.add_parser('service', help='Manage system service')
    parser_service_action =parser_service_subparsers.add_subparsers(help='Action', dest='action', required=False)
    parser_service_install = parser_service_action.add_parser('install', help='Install as a system service')
    #parser_install.add_argument('-e', '--env', dest='env', type=str, default=None, help='path to Python(>=3.8) executable')
    parser_service_uninstall = parser_service_action.add_parser('uninstall', help='Remove service')
    parser_service_start = parser_service_action.add_parser('start', help='Start service')
    parser_service_stop = parser_service_action.add_parser('stop', help='Stop service')
    parser_service_status = parser_service_action.add_parser('status', help='Service status')
    args = parser.parse_args()
    #args = parser.parse_args(['service', 'status'])

    if args.ip:
        settings.IP_ADDRESS = args.ip

    if args.port:
        settings.PORT = args.port

    if args.destination:
        settings.SCANS_FOLDER = args.destination

    if args.user:
        settings.USER = args.user

    if args.group:
        settings.GROUP = args.group

    settings.APP_FOLDER = f'{settings.ROOT_FOLDER}/{settings.APP_FOLDER}'

    if args.option == 'service' and args.action == 'install':
        write_conf(settings)
        if service_install(
            settings,
            #args.env or f'{prefix}/bin/python3',
            args.user or getpass.getuser(),
            args.group or getpass.getuser()
        ):
            print('Installed')
            sys.exit(0)
    elif args.option == 'service' and args.action == 'uninstall':
        if service_uninstall(
            settings
        ):
            print('Removed')
            sys.exit(0)
    elif args.option == 'service' and args.action == 'start':
        if service_start(
            settings
        ):
            print('Started')
            sys.exit(0)

    elif args.option == 'service' and args.action == 'stop':
        if service_stop(
            settings
        ):
            print('Stopped')
            sys.exit(0)
    elif args.option == 'service' and args.action == 'status':
        if service_status(
            settings
        ):
            sys.exit(0)

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
    if not args.nocfg:
        write_conf(settings)
    
    uvicorn.run(
        app, 
        host='0.0.0.0',
        port=int(settings.PORT),
        access_log=True,
        use_colors=True
    )

if __name__ == '__main__':
    main()