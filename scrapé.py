#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import httplib
from bs4 import BeautifulSoup
from bs4 import NavigableString

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial
    return inner

httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

class MediumSucks(object):

    def __init__(self):
        # Prepare request headers
        self.hdr = {
            'User-Agent'      : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset'  : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding' : 'none',
            'Accept-Language' : 'en-US,en;q=0.8',
            'Connection'      : 'keep-alive'
        }

    def __strip_tags(self, html):
        try:
            soup = BeautifulSoup(html)
        except UnicodeEncodeError:
            return ""

        for tag in soup.find_all(True):
            s = ""
            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = self.__strip_tags(unicode(c))
                s += unicode(c)

            tag.replaceWith(s)
        return soup

    def __get_http_response(self, url, url_param=None):
        req = urllib2.Request("{u}{up}".format(u=url, up=url_param if url_param else ''), headers=self.hdr)
        try:
            response = urllib2.urlopen(req, timeout=10)
        except httplib.IncompleteRead as e:
            # logging.warn("Partial read")
            response = e.partial
        except urllib2.HTTPError:
            # logging.warn("No response")
            response = None
        except urllib2.URLError:
            # logging.warn("There was a URL error")
            response = None

        return response

    def get_tag(self, tag):
        ahref = "https://www.medium.com/tag/{t}".format(t=tag)
        tag_articles = self.__get_http_response(ahref)
        for a in BeautifulSoup(tag_articles).find_all('a', {'class': 'block-linkHack'}):
            go_to_article = self.__get_http_response(a['href'])
            article_contents = BeautifulSoup(go_to_article).find_all("div", {'class': "postField"})
            print self.__strip_tags(unicode(article_contents[0]))


m = MediumSucks()
m.get_tag("tech")
