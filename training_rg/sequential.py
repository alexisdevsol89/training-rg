#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

from collections import deque
from random import Random

from shutil import copy2
from tabulate import tabulate

from training_rg.classifiers import WeekDay, KeyResp
from training_rg.constants import WEEKDAYS, SESSIONS_COUNT, SESSIONS_DAYS_OFF, SESSIONS_STEP

from training_rg.logger import logger


def sequence(dir_routines, count=30, first_day=WeekDay.MONDAY.value, days_off=1, step=0):
    """
    La idea es dada una lista, ordenada, de directorios con rutinas,
    generar cierta cantidad de sesiones, de entrenamiento, con determinados
    dias de descanso y a ciertos intervalos
    :param dir_routines: Lista de diretorios con las rutinas. El orden importa.
    :param count: Cantidad de sesiones
    :param first_day: Primer dia de la semana a considerar
    :param days_off: Dias de descanso
    :param step: Intervalos de entrenamiento
    :return: list de sesiones
    """
    if step < 1:
        step = len(dir_routines)

    sessions = []

    dir_routines_files = []
    for root in dir_routines:
        dir_routines_files.append(_walk(root))

    r = Random()

    j = 0
    for b in range(0, count, step + days_off):
        for day_i in range(b, b + step):
            day = WEEKDAYS[(first_day + day_i) % len(WEEKDAYS)]
            full_path = r.choice(dir_routines_files[j % len(dir_routines_files)])
            head, tail = os.path.split(full_path)
            sessions.append({'day': day, 'full_path': full_path, 'name': tail})
            j += 1

    return sessions


def parse_args():
    parser = argparse.ArgumentParser(prog='trg-seq',
                                     description='Generates training routines consecutively, with rest in between')

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s 1.0.0')
    parser.add_argument('-a',
                        '--author',
                        action='version',
                        version='%(prog)s was created by software developer Alexis Torres Valdes <alexisdevsol@gmail.com>',
                        help="Show program's author and exit")

    parser.add_argument('--dir-routines',
                        nargs='+',
                        required=True,
                        help='Routine directories. Order is important')
    parser.add_argument('--dir-output',
                        required=True,
                        help='Directory containing programmed routines')
    parser.add_argument('--first-day',
                        choices=WEEKDAYS,
                        required=False,
                        default=WEEKDAYS[0],
                        help=f'Directory containing programmed routines. Default: {WEEKDAYS[0]}')
    parser.add_argument('-c',
                        '--count',
                        type=int,
                        required=False,
                        default=SESSIONS_COUNT,
                        help=f'Number of sessions. Default: {SESSIONS_COUNT}')
    parser.add_argument('-s',
                        '--step',
                        type=int,
                        required=False,
                        default=SESSIONS_STEP,
                        help=f'Training sequence. Default: {SESSIONS_STEP}')
    parser.add_argument('-o',
                        '--days-off',
                        type=int,
                        required=False,
                        default=SESSIONS_DAYS_OFF,
                        help=f'Number of days without training. Default: {SESSIONS_DAYS_OFF}')
    parser.add_argument('-y',
                        '--yes',
                        action='store_true',
                        help='Answer yes to everything')
    parser.add_argument('-vv',
                        '--verbose',
                        action='store_true',
                        help='Show detailed information')

    return parser.parse_args()


def main():
    try:
        args = parse_args()
        arg_dir_routines = args.dir_routines
        arg_dir_output = args.dir_output
        arg_first_day = args.first_day
        arg_count = args.count
        arg_step = args.step
        arg_days_off = args.days_off
        arg_yes = args.yes
        arg_verbose = args.verbose

        # arg_dir_routines = [
        #     '/media/dev/cbc809ad-b091-4a86-9ac1-410e18469ead/media/entrenamiento/[Ejercicios] Fausto Murillo/1.fullbody/',
        #     '/media/dev/cbc809ad-b091-4a86-9ac1-410e18469ead/media/entrenamiento/[Ejercicios] Fausto Murillo/2.gap/',
        #     '/media/dev/cbc809ad-b091-4a86-9ac1-410e18469ead/media/entrenamiento/[Ejercicios] Fausto Murillo/3.abdominales/'
        # ]
        # arg_dir_output = '/media/dev/cbc809ad-b091-4a86-9ac1-410e18469ead/media/entrenamiento/Mis rutinas/dev/'
        # arg_first_day = 'Sunday'
        # arg_count = 30
        # arg_step = 3
        # arg_days_off = 1
        # arg_yes = False
        # arg_verbose = True

        if arg_verbose:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(ch)

        for path in arg_dir_routines:
            if not os.path.exists(path):
                raise ValueError(f"'{path}' directory does not exist")

        if not os.path.exists(arg_dir_output):
            raise ValueError(f"'{arg_dir_output}' directory does not exist")

        if arg_count and arg_count < 1:
            raise ValueError('The number of sessions must be greater than or equal to 1')

        if arg_step and arg_step < 1:
            raise ValueError('The training sequence has to be greater than or equal to 1')

        if arg_days_off and arg_days_off < 1:
            raise ValueError('At least 1 day without training is necessary')

        first_day = WEEKDAYS.index(arg_first_day)
        sessions = sequence(arg_dir_routines,
                            count=arg_count,
                            first_day=first_day,
                            days_off=arg_days_off,
                            step=arg_step)
        sessions_tab = [(i + 1, sessions[i]['day'], sessions[i]['name']) for i in range(len(sessions))]

        print('\nTraining Routine Sessions')
        print('=========================')
        print(tabulate(sessions_tab, headers=('#', 'Day', 'Routine')) + '\n')

        if not arg_yes:
            resp = _wait_resp('Would you like to copy the routines?')
        else:
            resp = KeyResp.YES.value

        if resp == KeyResp.YES.value:
            print('\nCopy routines...')
            print('================')
            _copy(sessions, arg_dir_output, lambda file_name_dst: print(file_name_dst))
            print('\nRoutines successfully copied!')
        elif resp == KeyResp.NO.value:
            sys.exit()
        else:
            raise ValueError(f'Only answers ({KeyResp.YES.value}/{KeyResp.NO.value}) are allowed')
    except Exception as err:
        logger.error(err)
        sys.exit(os.EX_SOFTWARE)


def _walk(path):
    files = []

    q = deque([path])
    while len(q):
        _dir = q.popleft()
        for item in os.scandir(_dir):
            if item.is_dir():
                q.append(item)
            else:
                files.append(item.path)

    return files


def _wait_resp(msg='Do you wish to continue?', k_yes=KeyResp.YES.value, k_no=KeyResp.NO.value):
    msg += ' (y/n): '
    text_input = input(msg).lower()
    while text_input != k_yes and text_input != k_no:
        text_input = input(msg).lower()

    return text_input


def _copy(sessions, to_dir, callback=None):
    copied = []

    for i in range(len(sessions)):
        src = sessions[i]['full_path']
        dst = os.path.join(to_dir, f"{i + 1}.{sessions[i]['day']} - {sessions[i]['name']}")
        copy2(src, dst)
        if callback:
            head, tail = os.path.split(dst)
            callback(tail)

    return copied


if __name__ == '__main__':
    main()
