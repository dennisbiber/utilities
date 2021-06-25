from __future__ import absolute_import
import contextlib
import os
import shutil
import tempfile  # stdlib provided

HARBORMASTER_PREFERRED_TMPDIR = "/var/drydock/tmp"


@contextlib.contextmanager
def temporary_file(*args, **kwargs):
    """Create and return an open temporary file

    Returns an open file with visibility in the file system; the name of
    the file is accessible as its 'path' attribute. This file will be
    automatically deleted when the context is exited.

        with tempfile.temporary_file() as f:
            ...

    :param mode: The open mode of the file
    :param dir: The directory to root the temporary file under
    :yields: An open file-like object
    """
    with tempfile.NamedTemporaryFile(*args, **kwargs) as f:
        # alias the name to the path attribute
        f.path = f.name
        yield f


@contextlib.contextmanager
def temporary_directory(*args, **kwargs):
    try:
        path = None
        path = tempfile.mkdtemp(*args, **kwargs)
        yield path
    finally:
        if path and os.path.exists(path):
            shutil.rmtree(path)


@contextlib.contextmanager
def temporary_amendment(log_index, amendment_name):
    try:
        yield
    finally:
        index_path = os.path.dirname(log_index)
        amendment_path = os.path.join(index_path, amendment_name)
        if os.path.exists(amendment_path):
            shutil.rmtree(amendment_path)