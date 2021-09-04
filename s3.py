import os
import logging
from io import BytesIO
from gzip import GzipFile
import mimetypes

from boto.s3.connection import S3Connection
from boto.s3.key import Key

__author__ = 'Dennis Biber'


log = logging.getLogger(__name__)


class S3Error(Exception):
    pass


class S3Util(object):

    def __init__(self, bucket, prefix, access_key_id, secret_access_key):
        """
        :param str bucket: the S3 bucket name
        :param str prefix: file path like prefix for all items we are inserting
        :param str access_key_id: AWS Key ID (must have proper S3 permissions for this bucket)
        :param str secret_access_key: AWS secret Key
        """
        # Connect to S3
        self._s3_conn = S3Connection(access_key_id, secret_access_key)

        # This is the bucket name and default prefix used for our data
        self._aws_prefix = prefix + ('' if prefix.endswith('/') else '/')

        # Get the bucket with the files (this will throw exceptions if the bucket is not found)
        self._s3_bucket = self._s3_conn.get_bucket(bucket)

    def has_key(self, path):
        return self._get_key(path) is not None

    def list_keys(self, path=None, force_slash=True):
        """
        :param str path: The sub path to list (trailing '/' will be automatically added)
        """

        filter_prefix = get_list_prefix(prefixer=self._get_key_path, path=path, force_slash=force_slash)

        return [k.key for k in self._s3_bucket.list(prefix=filter_prefix)]

    def upload_file(self, source_path, target_path, compress=False):
        """
        Upload the given file into the bucket.

        :param str source_path: path to the file to upload
        :param str target_path: the path inside our bucket (without prefix)
        """
        if not os.path.exists(source_path):
            raise S3Error('File "{f}" does not exist cannot write to: {b}'.format(f=source_path,
                                                                                  b=self._get_key_path(target_path)))

        key = self._make_key(target_path)
        log.info('Upload to: {} from file: {}'.format(key.name, source_path))

        if compress:
            headers = {'content-type': mimetypes.guess_type(source_path),
                       'content-encoding': 'gzip'}
            with get_gzip_compressed_file(source_path) as gz_data:
                key.set_contents_from_file(gz_data, headers)
        else:
            key.set_contents_from_filename(source_path)

        key.set_acl('public-read')

    def copy_keys(self, src_path, dst_path):
        """
        Recursively copy all keys that start with src to dst.

        :param str src_path: Where to recursively copy from (without prefix)
        :param str dst_path: Where the data is going (without prefix)
        """

        copy_keys(self, src_path=src_path, dst_path=dst_path)

    def delete_keys(self, path=None, force_slash=True):
        """
        Delete keys in bucket matching prefix (bucket name + aws prefix + path)

        :params str path: path inside bucket (without prefix)
        """
        for key in self.list_keys(path=path, force_slash=force_slash):
            log.info('Deleteing key: {}'.format(key))
            self._s3_bucket.delete_key(key)

    def print_keys(self, path=None, force_slash=True):
        """
        Print key in bucket matching prefix (bucket name + aws prefix + path)

         :params str path: path inside bucket (without prefix)
        """
        print "\nBucket Name: {}".format(self._s3_bucket.name)
        for key in self.list_keys(path=path, force_slash=force_slash):
            print key

    def download_file(self, target_path, source_path):
        """
        Download file(key) from bucket

        :param str source_path: the path inside our bucket (without prefix)
        :param str target_path: path containing name of the file where file needs to be download
        """
        key = self._get_key(source_path)
        if not key:
            raise S3Error("{} is not present in s3".format(self._get_key_path(key)))

        log.info('Downloading file to {} from {}'.format(target_path, source_path))

        key.get_contents_to_filename(target_path)

    def put_data(self, target_path, contents):
        """
        Put the given data into the bucket.

        :param str target_path: the path inside our bucket (without prefix)
        :param str contents: data to write
        """
        key = self._make_key(target_path)
        log.info('Write data to: {}'.format(key.name))

        key.set_contents_from_string(contents)
        key.set_acl('public-read')

    def get_data(self, path):
        """
        Get data at the given path in the bucket.

        :param str path: the path inside our bucket (without prefix)

        :return str: data from the path in the bucket
        """
        key = self._get_key(path)

        if key is None:
            raise S3Error('No data in: {}'.format(self._get_key_path(path)))

        log.info('Read data from: {}'.format(key.name))
        return key.get_contents_as_string()

    def copy_data(self, src_path, dst_path):
        """
        Copy data between given path in the bucket.

        :param str src_path: Where to copy from (without prefix)
        :param str dst_path: Where the data is going (without prefix)

        :return str: data from the path in the bucket
        """

        # Destination needs the leading '/' while the src does not
        dst = self._get_key_path(dst_path)
        src = self._get_key_path(src_path).lstrip('/')

        self._s3_bucket.copy_key(new_key_name=dst,
                                 src_bucket_name=self._s3_bucket.name,
                                 src_key_name=src)

    def _get_key(self, path):
        """
        Get the key for the given path if possible.

        :param str path: The path inside our bucket (without prefix)

        :return boto.s3.Key/None: The key if can be found, None otherwise
        """
        return self._s3_bucket.get_key(self._get_key_path(path))

    def _make_key(self, path):
        """
        Get the key for the given path, create if needed.

        :param str path: The path inside our bucket (without prefix)

        :return boto.s3.Key: the key
        """

        key = self._get_key(path)

        if key is None:
            key = Key(self._s3_bucket)
            key.key = self._get_key_path(path)

        return key

    def _get_key_path(self, path):
        """
        Return the full path inside the bucket given the suffix.

        :param str path: The path inside our bucket (without prefix)

        :return str: The full path inside the bucket.
        """
        return self._aws_prefix + path


class InMemoryS3(object):
    """
    Implements the same API as S3Util but stores things in memory
    useful for tests.
    """

    def __init__(self, data=None, prefix=None, **kwargs):
        '''
        :type data: dict
        :param data: Optional data to prime the in-memory bucket with
        :param prefix: see :class:`S3Util`
        :param kwargs: Keyword arguments to allow signature-matching of :class:`S3Util`, but are otherwise ignored
        '''
        self.data = {} if data is None else data

        # This is the bucket name and default prefix used for our data
        if prefix is None:
            self._aws_prefix = ''
        else:
            self._aws_prefix = prefix + ('' if prefix.endswith('/') else '/')

    def has_key(self, path):
        return self._get_key_path(path) in self.data

    def list_keys(self, path=None, force_slash=True):
        prefix = get_list_prefix(self._get_key_path, path=path, force_slash=force_slash)

        if prefix == '/':
            prefix = ''

        return [k for k in self.data.keys() if k.startswith(prefix)]

    def copy_keys(self, src_path, dst_path):
        copy_keys(self, src_path=src_path, dst_path=dst_path)

    def upload_file(self, target_path, source_path, compress=False):
        if compress:
            with get_gzip_compressed_file(source_path) as gz_data:
                self.data[self._get_key_path(target_path)] = gz_data.getvalue()
        else:
            self.data[self._get_key_path(target_path)] = read_file(source_path)

    def read_file(filename):
        fh = open(filename, "r")
        try:
            return fh.read()
        finally:
            fh.close()

    def download_file(self, target_path, source_path):
        with(open(target_path, 'w')) as f:
            f.write(self.data[self._get_key_path(source_path)])

    def put_data(self, target_path, contents):
        self.data[self._get_key_path(target_path)] = contents

    def get_data(self, path):
        return self.data[self._get_key_path(path)]

    def copy_data(self, src_path, dst_path):
        return self.put_data(dst_path, self.get_data(src_path))

    def _get_key_path(self, path):
        """
        Return the full path inside the bucket given the suffix.

        :param str path: The path inside our bucket (without prefix)

        :return str: The full path inside the bucket.
        """
        return self._aws_prefix + path

    def delete_keys(self, path=None, force_slash=True):
        """
        Delete keys in bucket matching prefix (bucket name + aws prefix + path)

        :params str path: path inside bucket (without prefix)
        """
        for key in self.list_keys(path, force_slash):
            self.data.pop(key)


def get_list_prefix(prefixer, path=None, force_slash=True):
    if path is None:
        path = ''

    filter_prefix = prefixer(path)

    if force_slash and not filter_prefix.endswith('/'):
        filter_prefix += '/'

    return filter_prefix.lstrip('/')


def copy_keys(s3, src_path, dst_path):
    """
    Copy keys between locations.

    :param str src_path: The sub path  (without prefix)
    :param str dst_path: The path inside our bucket (without prefix)
    """
    src_abs_path = s3._get_key_path(src_path).lstrip('/')
    abs_prefix = s3._aws_prefix.lstrip('/')

    for src_key in s3.list_keys(src_path):
        # This gives us back absolute paths, so we need to get back to relative
        # ones
        rel_path = os.path.relpath(src_key, src_abs_path)
        dst_key = os.path.join(dst_path, rel_path)

        src = os.path.relpath(src_key, abs_prefix)
        dst = dst_key
        log.info('Copy {} -> {}'.format(src, dst))

        s3.copy_data(src, dst)


def get_gzip_compressed_file(source_path):
    """
    Read in a file and return a gzip BytesIO object of the contents.

    :param str source_path: path to the file to compress

    :return bytes: The gzip compressed contents from source_path
    """
    gz_bytes = BytesIO()

    with open(source_path, 'rb') as source_file:
        file_contents = source_file.read()

        if file_contents is not None:
            gz_file = GzipFile(None, 'wb', 9, gz_bytes)
            gz_file.write(file_contents)
            gz_file.close()
            gz_bytes.seek(0)

    return gz_bytes
