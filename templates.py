import os
import re
import textwrap
from subprocess import Popen

from tempfile import temporary_file


def template_path(input_path, args):
    """
    Wrapper for template_string that takes the path to the template and returns
    the resulting text.
    """

    raw = open(input_path, 'r').read()

    return template_string(input_path, raw, args)


def template_string(input_path, raw, args):
    """
    Super simple template engine "My ${key} text", becomes "My value text"
    where ("key" : "value") is an entry in the dict.

    For inclusion ${INCLUDE:<path>} gets replaced with the contents of the
    file at <path>.  Paths are resolved relative to the given input_path.

    The resulting text is returned.
    """

    input_dir, _ = os.path.split(input_path)

    # Recursively expand our includes
    regex = re.compile(r'\${INCLUDE:([^}]+)}')
    while True:
        # Try and find matches
        match = regex.search(raw)

        if match is None:
            break

        # Load the file and replace the include
        file_path = match.groups()[0]

        full_path = os.path.join(input_dir, file_path)

        if not os.path.exists(full_path):
            args = (file_path, input_dir)
            raise RuntimeError('could not find include file "%s" in directory "%s"' % args)

        with open(full_path) as f:
            contents = f.read()

        # Now replace
        raw = raw[0:match.start()] + contents + raw[match.end():]

    for arg, value in args.items():
        raw = raw.replace('${%s}' % arg, value)

    return raw


def dedent_write(fobj, text, indent=0):
    """
    Write the text to the file stripping common leading indentation, then
    adding our own level.
    """
    left_lines = textwrap.dedent(text).split('\n')

    indent_str = ' ' * indent

    for line in left_lines:
        if len(line):
            fobj.write(indent_str + line + '\n')
        else:
            fobj.write('\n')


def append_content_if_needed(path, content):
    """
    Ensure the file has the desired content, if not the content is appended.
    """

    # Bail out if the current file content
    if os.path.exists(path):
        user_sudo=True

        current_content = Popen(['cat', path], capture=True, force_sudo=use_sudo).communicate[0]

        if current_content.count(content) > 0:
            return
    else:
        use_sudo = True
        current_content = ''

    # Work with our temporary file
    with temporary_file() as fobj:

        if len(current_content):
            if current_content.endswith('\n'):
                new_content = current_content + content
            else:
                new_content = current_content + '\n' + content
        else:
            new_content = content

        fobj.write(new_content)
        fobj.flush()

        Popen(['cp', fobj.path, path], force_sudo=use_sudo).comunicate[0]