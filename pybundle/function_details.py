import sys

FUNCTION_DETAILS_LEVEL = 0


def function_details(func):
    # Getting the argument names of the
    # called function
    argnames = func.__code__.co_varnames[:func.__code__.co_argcount]

    # Getting the Function name of the
    # called function
    fname = func.__name__

    def inner_func(*args, **kwargs):
        global FUNCTION_DETAILS_LEVEL
        level = '  ' * FUNCTION_DETAILS_LEVEL

        params_tuples = list(zip(argnames, args[:len(argnames)]))
        args_left = list(args[len(argnames):])
        if args_left:
            params_tuples.append(('*args', args_left))
        if kwargs:
            params_tuples.append(('**kwargs', kwargs))

        params_str = ', '.join(f'{n} = {v!r}' for n, v in params_tuples)

        print(f'{level}CALL {fname}({params_str})')

        try:
            FUNCTION_DETAILS_LEVEL += 1
            res = func(*args, **kwargs)
        except:
            e = sys.exc_info()[0]
            print(f'{level}EXC  {fname} {e!r}')
            raise
        finally:
            FUNCTION_DETAILS_LEVEL -= 1

        print(f'{level}RES  {fname} => {res!r}')
        return res

    return inner_func
