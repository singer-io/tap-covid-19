import re
from datetime import datetime
import time
import backoff
import requests
from requests.exceptions import ConnectionError
import singer
from singer import metrics, utils

LOGGER = singer.get_logger()


class Server5xxError(Exception):
    pass


class Server429Error(Exception):
    pass


class AbuseDetection403Error(Exception):
    pass


class Server304Error(Exception):
    pass


class GitError(Exception):
    pass


class GitBadRequestError(GitError):
    pass


class GitUnauthorizedError(GitError):
    pass


class GitRequestFailedError(GitError):
    pass


class GitNotFoundError(GitError):
    pass


class GitMethodNotAllowedError(GitError):
    pass


class GitConflictError(GitError):
    pass


class GitForbiddenError(GitError):
    pass


class GitUnprocessableEntityError(GitError):
    pass


class GitInternalServiceError(GitError):
    pass


ERROR_CODE_EXCEPTION_MAPPING = {
    400: GitBadRequestError,
    401: GitUnauthorizedError,
    402: GitRequestFailedError,
    403: GitForbiddenError,
    404: GitNotFoundError,
    405: GitMethodNotAllowedError,
    409: GitConflictError,
    422: GitUnprocessableEntityError,
    500: GitInternalServiceError}


def get_exception_for_error_code(error_code):
    return ERROR_CODE_EXCEPTION_MAPPING.get(error_code, GitError)

def raise_for_error(response):
    LOGGER.error('ERROR {}: {}, REASON: {}'.format(response.status_code,\
        response.text, response.reason))
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        try:
            content_length = len(response.content)
            if content_length == 0:
                # There is nothing we can do here since Git has neither sent
                # us a 2xx response nor a response content.
                return
            response = response.json()
            if ('error' in response) or ('errorCode' in response):
                message = '%s: %s' % (response.get('error', str(error)),
                                      response.get('message', 'Unknown Error'))
                error_code = response.get('status')
                ex = get_exception_for_error_code(error_code)
                raise ex(message)
            else:
                raise GitError(error)
        except (ValueError, TypeError):
            raise GitError(error)


class GitClient(object):
    def __init__(self,
                 api_token,
                 user_agent=None):
        self.__api_token = api_token
        self.base_url = "https://api.github.com"
        self.__user_agent = user_agent
        self.__session = requests.Session()
        self.__verified = False

    def __enter__(self):
        self.__verified = self.check_access()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__session.close()

    @backoff.on_exception(backoff.expo,
                          Server5xxError,
                          max_tries=5,
                          factor=2)
    def check_access(self):
        if self.__api_token is None:
            raise Exception('Error: Missing api_token in config.json.')
        headers = {}
        # Endpoint: simple API call to return a single record (current User) to test access
        url = 'https://api.github.com/user'
        if self.__user_agent:
            headers['User-Agent'] = self.__user_agent
        headers['Accept'] = 'application/vnd.github.v3+json'
        # Authentication: https://developer.github.com/v3/#authentication
        headers['Authorization'] = 'Token {}'.format(self.__api_token)
        response = self.__session.get(
            url=url,
            headers=headers)
        if response.status_code != 200:
            LOGGER.error('Error status_code = {}'.format(response.status_code))
            raise_for_error(response)
        else:
            return True


    @backoff.on_exception(backoff.expo,
                          (Server5xxError, ConnectionError, Server429Error, AbuseDetection403Error),
                          max_tries=7,
                          factor=3)
    # Rate Limiting: https://developer.github.com/v3/#rate-limiting
    @utils.ratelimit(5000, 3600)
    def request(self, method, url=None, path=None, headers=None, json=None, version=None, **kwargs):
        if not self.__verified:
            self.__verified = self.check_access()

        if not url and path:
            url = '{}/{}'.format(self.base_url, path)

        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            del kwargs['endpoint']
        else:
            endpoint = None

        if not headers:
            headers = {}

        # API Version: https://developer.github.com/v3/#current-version
        if not version:
            version = 'v3'
        headers['Accept'] = 'application/vnd.github.{}+json'.format(version)

        # Authentication: https://developer.github.com/v3/#authentication
        headers['Authorization'] = 'Token {}'.format(self.__api_token)

        if self.__user_agent:
            headers['User-Agent'] = self.__user_agent

        if method == 'POST':
            headers['Content-Type'] = 'application/json'

        with metrics.http_request_timer(endpoint) as timer:
            response = self.__session.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                **kwargs)
            timer.tags[metrics.Tag.http_status_code] = response.status_code

        if response.status_code >= 500:
            raise Server5xxError()

        # Pagination: https://developer.github.com/v3/guides/traversing-with-pagination/
        links_header = response.headers.get('Link')
        links = []
        next_url = None
        if links_header:
            links = links_header.split(',')
        for link in links:
            try:
                url, rel = re.search(r'^\<(https.*)\>; rel\=\"(.*)\"$', link.strip()).groups()
                if rel == 'next':
                    next_url = url
            except AttributeError:
                next_url = None

        # last-modified: https://developer.github.com/v3/#conditional-requests
        last_modified = response.headers.get('Last-Modified')
        last_modified_str = None
        if last_modified:
            last_modified_dttm = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
            last_modified_str = last_modified_dttm.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 304: File Not Modified status_code
        if response.status_code == 304:
            LOGGER.warning('304: FILE NOT UPDATED, Stream: {}, URL: {}'.format(endpoint, url))
            return None, next_url, last_modified_str
        # Catch 403 error with message:
        #  "You have triggered an abuse detection mechanism. Please wait a few minutes before you try again."
        # Reference: https://developer.github.com/v3/#abuse-rate-limits
        if response.status_code == 403:
            response_json = response.json()
            response_message = response_json.get('message', '')
            if 'abuse detection mechanism.' in response_message:
                # Wait 3 minutes
                LOGGER.warning('Abuse Detection 403 Error: API triggered an abuse detection mechanism. Waiting 3 mins and trying again.')
                time.sleep(180) # Wait for 3 minutes
                raise AbuseDetection403Error(response)

        if response.status_code != 200:
            raise_for_error(response)

        response_json = response.json()

        return response_json, next_url, last_modified_str

    def get(self, url=None, path=None, headers=None, **kwargs):
        return self.request('GET', url=url, path=path, headers=headers, **kwargs)

    def post(self, url=None, path=None, headers=None, **kwargs):
        return self.request('POST', url=url, path=path, headers=headers, **kwargs)
