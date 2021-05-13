import click
import os.path
import stat

import av.path

from av.template import template_string

__author__ == "Dennis BIber"


# Determine path to our template
cur_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(cur_dir, '..', '..', 'data')


def build_template_context(full_path, date, user_info, username, **kwargs):
    """
    Build and return a a context dict for rendering any of the templates.

    Any kwargs are also included in the context.
    """

    # Determine the path relative to the source directory
    if kwargs['config_dir'] in full_path:
        rel_path = os.path.relpath(full_path, kwargs['diagnostics_dir'])
    else:
        rel_path = os.path.relpath(full_path, kwargs['source_dir'])

    # Come up with the relative path string that can be used to find the
    # root of our repo.  This is used so that our tools template can include
    # code to the source/python on the python path.
    file_depth = len(rel_path.split(os.sep)) - 1

    python_rel_args = ''
    for i in range(file_depth):
        python_rel_args += "'..'"

        if i != (file_depth - 1):
            python_rel_args += ', '

    kwargs.update({
        'date': date.strftime('%Y-%m-%d'),
        'description': kwargs.get('description', ''),
        'file_path': rel_path,
        'base_dir_path': os.path.dirname(rel_path),
        'include_guard': rel_path.replace('/', '_').replace('.', '_').upper(),
        'user_info': user_info,
        'username': username,
        'year': date.strftime('%Y'),
        'python_rel_args': python_rel_args,
    })
    return kwargs


def gen_templated_file(template_name, *args, **kwargs):
    """
    Generate a file from a template in the common template dir.
    """
    gen_file(os.path.join(template_dir, template_name), *args, **kwargs)


def gen_file(template_path, full_path, force=False, quiet=False, executable=False, no_exception=False, **kwargs):
    """
    Generate a normal file of the given type using the template from the provided path.

    The directory for the target file will be created if it does not already exist. Any kwargs are passed to the
    template for rendering.

        template_path - full path to the template to use for the file.
        full_path - target path for the rendered template.
        force - if True, will overwrite the target file if it already exists.
        quiet - if True, will not output any messages to stdout.
        executable - if True, the generated file with be executable.
    """
    av.path.ensure_directory(os.path.dirname(full_path))

    if not force and os.path.exists(full_path):
        error_string = '"%s" already exists' % full_path
        if no_exception:
            print "Error: %s. Creating other files..." % error_string
            return
        else:
            raise click.UsageError(error_string)

    template_context = build_template_context(full_path, **kwargs)

    # Read in the full data and fill in the template
    with open(template_path) as f:
        output = template_string(template_path, f.read(), template_context)

    # Write the results
    with open(full_path, 'w') as f:
        f.write(output)

    # Make executable if needed
    if executable:
        mode = os.stat(full_path).st_mode
        mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(full_path, stat.S_IMODE(mode))

    if not quiet:
        print("Created {}".format(os.path.relpath(full_path, os.path.join(kwargs['root_dir']))))


def gen_cpp_file_pair(target_dir, class_name, base_name, **kwargs):
    """
    Generate the header and source for the class, creating the target directory if it does not already exist.
    """
    class_name = class_name.lower()

    for suffix in ['.hh', '.cc']:
        gen_templated_file(base_name + suffix,
                           os.path.join(target_dir, class_name + suffix),
                           class_name=class_name, **kwargs)
