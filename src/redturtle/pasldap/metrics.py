# https://github.com/mamico/mrs.doubtfire/blob/main/src/mrs/doubtfire/meta.py
from redturtle.pasldap import logger
from time import time
from zope.globalrequest import getRequest

import functools
import traceback


def emoji_by_elapsed(elapsed):
    if elapsed < 20:
        return "\U0001F60E"  # GOOD
    elif elapsed < 100:
        return "\U0001F914"  # MUMBLE
    else:
        return "\U0001F4A9"  # SHIT


def sanitize_kwargs(kwargs):
    return {
        k: v if k not in ("secret", "password", "token") else "***"
        for k, v in kwargs.items()
    }


# http://stackoverflow.com/questions/3931627/how-to-build-a-python-decorator-with-optional-parameters
def metricmethod(*args, **kwargs):
    info = None
    fname = None

    def _metricmethod(f):
        # AttributeError: 'BoundPageTemplate' object has no attribute '__name__'
        if not hasattr(f, "__name__"):
            return f

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # import pdb; pdb.set_trace()
            try:
                if fname is None:
                    func_name = f.__name__
                else:
                    func_name = fname
                func_full_name = f"{f.__module__}.{func_name}"
            except AttributeError:
                func_full_name = f.__self__.__name__
            start = time()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed = int((time() - start) * 1000.0)
                if elapsed > threshold:
                    if level in ("debug", "trace"):
                        sanitized_kwargs = sanitize_kwargs(kwargs)
                        logger.info(
                            "Request URL: {}".format(getRequest().get("URL", ""))
                        )
                        logger.info(
                            "func=%s info=%s args=%s kwargs=%s elapsed=%sms threshold=%sms %s",
                            func_full_name,
                            info(*args, **sanitized_kwargs) if callable(info) else info,
                            args,
                            sanitized_kwargs,
                            elapsed,
                            threshold,
                            emoji_by_elapsed(elapsed),
                        )
                    else:
                        logger.info(
                            "func=%s info=%s elapsed=%sms threshold=%sms %s",
                            func_full_name,
                            info,
                            elapsed,
                            threshold,
                            emoji_by_elapsed(elapsed),
                        )
                    if level == "trace":
                        logger.info("".join(traceback.format_stack()[:-1]))

        return wrapper

    if (
        "threshold" not in kwargs
        and "level" not in kwargs
        and "info" not in kwargs
        and "fname" not in kwargs
        and callable(args[0])
    ):
        # No arguments, this is the decorator
        # Set default values for the arguments
        threshold = -1
        level = "debug"
        info = None
        fname = None
        return _metricmethod(args[0])
    else:
        # This is just returning the decorator
        threshold = kwargs.get("threshold", -1)
        level = kwargs.get("level", "debug")
        info = kwargs.get("info", None)
        fname = kwargs.get("fname", None)
        return _metricmethod
