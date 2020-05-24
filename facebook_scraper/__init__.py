import csv
import logging
import sys
from typing import Iterator, Tuple, Union

from .constants import DEFAULT_REQUESTS_TIMEOUT
from .facebook_scraper import FacebookScraper
from .typing import Post


_scraper = FacebookScraper()


def get_posts(
    account: str = None,
    group: Union[str, int] = None,
    credentials: Tuple[str, str] = None,
    **kwargs,
) -> Iterator[Post]:
    valid_args = sum(arg is not None for arg in (account, group))

    if valid_args != 1:
        raise ValueError("You need to specify either account or group")

    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)

    options = kwargs.setdefault('options', set())

    # TODO: Deprecate `pages` in favor of `page_limit` since it is less confusing
    if 'pages' in kwargs:
        kwargs['page_limit'] = kwargs.pop('pages')

    # TODO: Deprecate `extra_info` in favor of `options`
    if 'extra_info' in kwargs:
        kwargs.pop('extra_info')
        options.add('reactions')

    if credentials is not None:
        _scraper.login(*credentials)

    if account is not None:
        return _scraper.get_posts(account, **kwargs)

    elif group is not None:
        return _scraper.get_group_posts(group, **kwargs)


def write_posts_to_csv(
    account: str = None, group: Union[str, int] = None, filename=None, **kwargs
):
    """
    :param account:     Facebook account name e.g. "nike", string
    :param group:       Facebook group id
    :param filename:    File name, defaults to <<account_posts.csv>>
    :param pages:       Number of pages to scan, integer
    :param timeout:     Session response timeout in seconds, integer
    :param sleep:       Sleep time in s before every call, integer
    :param credentials: Credentials for login - username and password, tuple
    :return:            CSV written in the same location with <<account_name>>_posts.csv
    """
    list_of_posts = list(get_posts(account=account, group=group, **kwargs))

    if not list_of_posts:
        print("Couldn't get any posts.", file=sys.stderr)
        return

    keys = list_of_posts[0].keys()

    if filename is None:
        filename = str(account or group) + "_posts.csv"

    with open(filename, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_posts)


def _main():
    """facebook-scraper entry point when used as a script"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('account', type=str, help="Facebook account")
    parser.add_argument('-f', '--filename', type=str, help="Output filename")
    parser.add_argument('-p', '--pages', type=int, help="Number of pages to download", default=10)

    args = parser.parse_args()

    write_posts_to_csv(account=args.account, filename=args.filename, pages=args.pages)


if __name__ == '__main__':
    _main()


# Disable logging by default
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
