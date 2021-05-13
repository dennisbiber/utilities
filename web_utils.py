import errno
import getpass
import os
import sys

import requests

__author__ = 'Dennis Biber'

_API_KEY_PATH = ""

_MAX_RETRIES = 5
_DEFAULT_RETRIES = 3
_DEFAULT_DELAY_S = 0
_DEFAULT_TIMEOUT_S = 5.0


class LoginFailed(Exception):
    '''
    An exception that is raised for a failed login after the maximum retry attempts
    '''


class NoCredentials(Exception):
    '''
    An exception that is thrown if there are no cached credentials and an interactive login is not allowed
    '''


class WebServiceInterface(object):
    def __init__(self, server_login_url, api_key="", api_key_file="", timeout=_DEFAULT_TIMEOUT_S, allow_prompt=True):
        '''
        Initialize a web interface object. Initialization does not perform a login. Either login using the login method
        or by retrieving the session property.

        :param server_login_url: The url of the web server's login endpoint
        :param api_key: An optional api token to use for logging in
        :param api_key_file: An optional filename from which an api key can be loaded
        :param timeout: The timeout to use for the login
        :param allow_prompt: A boolean to allow or disallow interactive logins if no credentials are found or specified
        '''
        self._webauth = _WebAuth(server_login_url, api_key, api_key_file, timeout, allow_prompt)

    @property
    def api_key(self):
        return self._webauth.api_key

    @property
    def session(self):
        return self._webauth.session

    @property
    def timeout(self):
        return self._webauth.timeout

    @timeout.setter
    def timeout(self, timeout):
        self._webauth.timeout = timeout

    def login(self, retries=_DEFAULT_RETRIES):
        '''
        Log in to the configured web service. Will raise a requests.HTTPError if there is a HTTP Error

        :param retries: The number of retries before failing if login is required/allowed
        '''
        self._webauth.login(retries)


class _WebAuth(object):
    '''
    An auth client that maintains a requests.session for interfacing to web services
    '''

    def __init__(self, server_login_url, api_key="", api_key_file="", timeout=_DEFAULT_TIMEOUT_S, allow_prompt=True):
        '''
        Initialize a web auth object. Initialization does not perform a login. Either login using the login method
        or by retrieving the session property.

        :param server_login_url: The url of the web server's login endpoint
        :param api_key: An optional api token to use for logging in
        :param api_key_file: An optional filename from which an api key can be loaded
        :param timeout: The timeout to use for the login
        :param allow_prompt: A boolean to allow or disallow interactive logins if no credentials are found or specified
        '''
        self._server_login_url = server_login_url
        self._timeout = timeout
        self._allow_prompt = allow_prompt
        self._session = None
        self._api_key = ""

        if api_key:
            self._api_key = api_key

        elif api_key_file:
            try:
                key_from_file = self._api_key_from_file(api_key_file)

                if key_from_file:
                    self._api_key = key_from_file

            except IOError as err:
                sys.stderr.write("Unable to read the key file {0}: {1}\n".format(api_key_file, os.strerror(err.errno)))

    def __del__(self):
        # Exceptions in __del__ are already ignored, but the try/except will prevent an error from printing every time
        try:
            self._close_session()
        except TypeError:
            pass
        except AttributeError:
            pass

    @property
    def api_key(self):
        return self._api_key

    def _close_session(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    def _local_api_key_file_for_user(self, user=""):
        '''
        Get the default catalog key file for the passed in user

        :param user: Optional user name to get the key file for. If not specified, defaults to getpass.getuser()
        '''
        user_home = os.path.expanduser("~{0}".format(getpass.getuser() if not user else user))
        return os.path.join(user_home, _API_KEY_PATH)

    def _api_key_from_file(self, key_file):
        '''
        Return the cached Catalog API key from the passed in file

        :param key_file: The full path to a catalog key file
        '''
        with open(key_file, 'rb') as api_key_file:
            return api_key_file.read().splitlines()[0]

    def _save_api_key_to_file(self, key_file, api_key):
        '''
        Save the passed in key to the passed in key file

        :param key_file: The full path to a catalog key file
        :param api_key: The catalog key to save to the file
        '''

        try:
            os.makedirs(os.path.dirname(key_file), 0o755)

        except OSError as err:
            if err.errno != errno.EEXIST:
                raise

        with open(key_file, 'wb') as api_key_file:
            api_key_file.write(api_key)

    def _save_session_api_key_to_file(self, key_file):
        '''
        Save the current login session's token to the passed in key file. The login token
        matches the api key for the current user.

        :param key_file: The full path to a catalog key file
        '''
        if self._session is not None:
            try:
                self._save_api_key_to_file(key_file, self._session.cookies["remember_token"].strip("\"'"))

            except KeyError:
                sys.stderr.write("Current session does not have a token that can be saved\n")
                pass

    @property
    def session(self):
        if self._session is None:
            self.login()

        return self._session

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        if isinstance(timeout, (float, int, long)):
            if timeout != self._timeout:
                self._timeout = float(timeout)

        else:
            raise TypeError("timeout must be a float not {0}".format(timeout.__class__.__name__))

    def login(self, retries=_DEFAULT_RETRIES):
        '''
        Log in to the configured web service. Will raise a requests.HTTPError if there is a HTTP Error

        :param retries: The number of retries before failing if login is required/allowed
        '''
        if self._session is not None:
            self._close_session()

        session = requests.Session()
        if self._api_key:
            # If there is already an API key, just use it for every call in the session
            session.params = {"apikey": self._api_key}
            self._session = session
            return

        # Try to read the local user's default catalog API key file
        user_api_key_file_path = self._local_api_key_file_for_user()

        try:
            self._api_key = self._api_key_from_file(user_api_key_file_path)
            return self.login(retries)

        except IOError:
            sys.stderr.write("Could not read the local API file {0}\n".format(user_api_key_file_path))
            pass

        if not self._allow_prompt:
            raise NoCredentials("There are no cached credentials and interactive login is not allowed")

        # If there is no passed in key and no key file, prompt for an interactive login
        while retries > 0:
            user = raw_input("LDAP User [{0}]: ".format(getpass.getuser()))
            if not user:
                user = getpass.getuser()

            password = getpass.getpass("LDAP Password for {0}: ".format(user))

            response = session.post(self._server_login_url, data={
                                    "username": user, "password": password}, timeout=self._timeout)
            response.raise_for_status()

            retries -= 1
            if retries > 0:
                print("Failed to login. {0} login atempt{1} remaining".format(retries, "s" if retries > 1 else ""))

        if self._session is None:
            raise LoginFailed("Exceeded maximum number of login attempts")

        # Save the current user's login information to the default key path if the user and default user are the same
        if user == getpass.getuser():
            try:
                self._save_session_api_key_to_file(user_api_key_file_path)

            except IOError as err:
                if err.errno == errno.EACCES:
                    sys.stderr.write(
                        "Cannot write the current user's api key file: {0}\n".format(os.strerror(err.errno)))

                else:
                    raise


def _request_wrapper(method_type, url, session, retries, delay, timeout, params=None, data=None):
    """
    Execute an http request with error handling and parameterized retries
    :param method: Request method (get, post, put, head, patch, delete)
    :param url: url for request
    :param retries: Number of retries to attempt
    :param delay: Time to wait before retry
    :param timeout: Timeout for the request in seconds
    :param kwargs: Dictionary of parameters that are specific to each request (ie. json for post)
    :return: Return JSON for response object
    """

    # Attempt request with retries (capped at max)
    retries = max(0, min(retries, _MAX_RETRIES))

    # Identify appropriate request
    method = method_type.lower()
    if session is not None:
        request_method = getattr(session, method)
    else:
        request_method = getattr(requests, method)

    # Attempt request with retries (capped at max)
    retries = max(0, min(retries, _MAX_RETRIES))

    while retries >= 0:
        try:
            if method == "get":
                response = request_method(url, params=params)
            elif method == "post" or method == "put":
                response = request_method(url, json=data)
            elif method == "delete":
                response = request_method(url)
            else:
                raise ValueError("{0} method is not currently a supported method".format(method))

            response.raise_for_status()

        except requests.exceptions.RequestException as err:

            if retries > 0:
                if isinstance(err, requests.ConnectionError):
                    print("Connection Error Occured. Retrying...")
                elif isinstance(err, requests.Timeout):
                    print("Request Timeout Occured. Retrying...")
                else:
                    print("Failed Request: {0}".format(url))
                    raise
            else:
                print("Failed Request: {0}".format(url))
                raise
        else:
            break

        retries -= 1

    # Return response JSON
    try:
        response_json = response.json()

    except ValueError:
        print("JSON Decode Error For Request: {0}".format(response.url))
        raise

    return response_json


def http_get(url, session=None, params=None,
             retries=_DEFAULT_RETRIES, delay=_DEFAULT_DELAY_S, timeout=_DEFAULT_TIMEOUT_S):
    """
    Function to execute http get() request with error handling and parameterized retries
    If a session is provided the session will be used for the request.

    :param session: a requests.session() object
    :param url: The url string for the get request
    :param params: A dict defining key, value pairs for the parameters of the get request
    :param retries: Number of retries to attempt
    :param delay: Time to wait before retry
    :param timeout: Timeout for the request in seconds
    :return: Return JSON for response data
    """

    # Remove empty parameters
    if params:
        params = dict((k, v) for k, v in params.iteritems() if v)

        # Update session parameters if session is provided
        if session is not None:
            session.params.update(params)

    return _request_wrapper("get", url, session, retries, delay, timeout, params=params)


def http_post(url, session=None, data=None,
              retries=_DEFAULT_RETRIES, delay=_DEFAULT_DELAY_S, timeout=_DEFAULT_TIMEOUT_S):
    """
    Function to execute http post() request with error handling and parameterized retries
    If a session is provided the session will be used for the request.
    Post assumes JSON data and request header content type is set to application/json

    :param url: The url string for the get request
    :param session: a requests.session() object
    :param json: Dictoonary representing json data to be posted
    :param retries: Number of retries to attempt
    :param delay: Time to wait before retry
    :param timeout: Timeout for the request in seconds
    :return: Return JSON for response data
    """

    # Attempt error handled post
    return _request_wrapper("post", session, retries, delay, timeout, data=data)


def http_put(url, session=None, data=None,
             retries=_DEFAULT_RETRIES, delay=_DEFAULT_DELAY_S, timeout=_DEFAULT_TIMEOUT_S):
    """
    Function to execute http put() request with error handling and parameterized retries
    If a session is provided the session will be used for the request.
    Post assumes JSON data and request header content type is set to application/json

    :param url: The url string for the put request
    :param session: a requests.session() object
    :param json: Dictoonary representing json data to be posted
    :param retries: Number of retries to attempt
    :param delay: Time to wait before retry
    :param timeout: Timeout for the request in seconds
    :return: Return JSON for response data
    """

    # Attempt error handled post
    return _request_wrapper("put", url, session, retries, delay, timeout, data=data)


def http_delete(url, session=None, retries=_DEFAULT_RETRIES, delay=_DEFAULT_DELAY_S, timeout=_DEFAULT_TIMEOUT_S):
    """
    Function to execute http delete() request with error handling and parameterized retries
    If a session is provided the session will be used for the request.

    :param url: The url string for the get request
    :param session: a requests.session() object
    :param retries: Number of retries to attempt
    :param delay: Time to wait before retry
    :param timeout: Timeout for the request in seconds
    :return: Return JSON for response data
    """

    # Attempt error handled post
    return _request_wrapper("delete", url, session, retries, delay, timeout)
