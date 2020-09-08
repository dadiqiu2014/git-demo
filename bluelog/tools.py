try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import url_for, redirect, request, current_app


def is_safe_url(target):
    """
    验证连接是否安全是否是本站的连接
    :param target:
    :return:
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next', ), request.referrer:
        if not target:
            continue

        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


if __name__ == '__main__':

    # print(urljoin('http://0.0.0.0:9999', 'hello_world/page1'))
    print(urlparse("http://www.baidu.com/page/one?page=1#comment"))
    # for n in 1, 2:
    #     print(n)
