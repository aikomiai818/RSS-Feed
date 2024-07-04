from httpx import AsyncClient
from asyncio import (
    create_subprocess_exec,
    create_subprocess_shell,
    run_coroutine_threadsafe,
    sleep,
)
from asyncio.subprocess import PIPE
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

from bot import user_data, config_dict, bot_loop

THREADPOOL = ThreadPoolExecutor(max_workers=1000)


def arg_parser(items, arg_base):
    if not items:
        return
    bool_arg_set = {
        "-b", "-e", "-z", "-s", "-j", "-d", "-sv", "-ss", "-f", "-fd",
        "-fu", "-sync", "-ml"
    }
    t = len(items)
    i = 0
    arg_start = -1

    while i < t:
        part = items[i]
        if part in arg_base:
            if arg_start == -1:
                arg_start = i
            if (i + 1 == t and part in bool_arg_set) or part in bool_arg_set:
                arg_base[part] = True
            else:
                sub_list = []
                for j in range(i + 1, t):
                    item = items[j]
                    if item in arg_base:
                        if part in bool_arg_set and not sub_list:
                            arg_base[part] = True
                        break
                    sub_list.append(item)
                    i += 1
                if sub_list:
                    arg_base[part] = " ".join(sub_list)
        i += 1

    if "link" in arg_base and items[0] not in arg_base:
        link = items[:arg_start] if arg_start != -1 else items
        if link:
            arg_base["link"] = " ".join(link)


async def retry_function(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except Exception:
        return await retry_function(func, *args, **kwargs)


async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    try:
        stdout = stdout.decode().strip()
    except UnicodeDecodeError:
        stdout = "Unable to decode the response!"
    try:
        stderr = stderr.decode().strip()
    except UnicodeDecodeError:
        stderr = "Unable to decode the error!"
    return stdout, stderr, proc.returncode


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREADPOOL, pfunc)
    return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def new_thread(func):
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper