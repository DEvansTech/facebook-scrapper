import codecs
import re
from datetime import datetime
from typing import Optional
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse, urlunparse

import dateparser
import lxml.html
from bs4 import BeautifulSoup
from requests_html import DEFAULT_URL, Element, PyQuery


def find_and_search(node, selector, pattern, cast=str):
    container = node.find(selector, first=True)
    match = container and pattern.search(container.html)
    return match and cast(match.groups()[0])


def parse_int(value: str) -> int:
    return int(''.join(filter(lambda c: c.isdigit(), value)))


def decode_css_url(url: str) -> str:
    url = re.sub(r'\\(..) ', r'\\x\g<1>', url)
    url, _ = codecs.unicode_escape_decode(url)
    return url


def filter_query_params(url, whitelist=None, blacklist=None) -> str:
    def is_valid_param(param):
        if whitelist is not None:
            return param in whitelist
        if blacklist is not None:
            return param not in blacklist
        return True  # Do nothing

    parsed_url = urlparse(url)
    query_params = parse_qsl(parsed_url.query)
    query_string = urlencode([(k, v) for k, v in query_params if is_valid_param(k)])
    return urlunparse(parsed_url._replace(query=query_string))


def make_html_element(html: str, url=DEFAULT_URL) -> Element:
    pq_element = PyQuery(html)[0]  # PyQuery is a list, so we take the first element
    return Element(element=pq_element, url=url)


month = (
    r"Jan(?:uary)?|"
    r"Feb(?:ruary)?|"
    r"Mar(?:ch)?|"
    r"Apr(?:il)?|"
    r"May|"
    r"Jun(?:e)?|"
    r"Jul(?:y)?|"
    r"Aug(?:ust)?|"
    r"Sep(?:tember)?|"
    r"Oct(?:ober)?|"
    r"Nov(?:ember)?|"
    r"Dec(?:ember)?"
)
day_of_month = r"\d{1,2}"
specific_date = f"(?:{month}) {day_of_month}" + r"(?:, \d{4})?"

date = f"{specific_date}|Today|Yesterday"

hour = r"\d{1,2}"
minute = r"\d{2}"
period = r"AM|PM"

exact_time = f"(?:{date}) at {hour}:{minute} (?:{period})"
relative_time_hours = r"\b\d{1,2} ?h(?:rs?)?"
relative_time_mins = r"\b\d{1,2} ?mins?"
relative_time = f"{relative_time_hours}|{relative_time_mins}"

datetime_regex = re.compile(fr"({exact_time}|{relative_time})")


def parse_datetime(text: str) -> Optional[datetime]:
    time_match = datetime_regex.search(text)
    if time_match:
        time = time_match.group(0)
        return dateparser.parse(time)
    else:
        return None


def html_element_to_string(element: Element, pretty=False) -> str:
    html = lxml.html.tostring(element.element, encoding='unicode')
    if pretty:
        html = BeautifulSoup(html, features='html.parser').prettify()
    return html
