from typing import Callable, Optional


def do_while(func: Callable, condition: Callable[..., bool],
             func_args: tuple = (), cond_args: tuple = ()):
    result = func(*func_args, None)
    while condition(*cond_args, result):
        result = func(*func_args, result)
    return result


def do_while_no_return_arg(func: Callable, condition: Callable[..., bool],
                           func_args: tuple = (), cond_args: tuple = ()):
    result = func(*func_args)
    while condition(*cond_args, result):
        result = func(*func_args)
    return result
