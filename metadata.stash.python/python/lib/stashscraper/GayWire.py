import json
import sys

try:
    from urllib2 import Request, urlopen
except ImportError:
    from urllib.request import Request, urlopen

try:
    from ..py_common import log
    from ..py_common.util import replace_all, replace_at
    from ..AyloAPI.scrape import (
        gallery_from_url,
        scraper_args,
        scene_from_url,
        scene_search,
        scene_from_fragment,
        performer_from_url,
        performer_from_fragment,
        performer_search,
        movie_from_url,
    )
except ImportError:
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from py_common import log
    from py_common.util import replace_all, replace_at
    from AyloAPI.scrape import (
        gallery_from_url,
        scraper_args,
        scene_from_url,
        scene_search,
        scene_from_fragment,
        performer_from_url,
        performer_from_fragment,
        performer_search,
        movie_from_url,
    )

studio_map = {
    "Its Gonna Hurt": "It's Gonna Hurt",
    "Poundhisass": "Pound His Ass",
}


def redirect(url):
    """Follow redirects using HEAD request with urllib"""
    if not url or "gaywire.com/scene/" not in url:
        return url
    
    try:
        request = Request(url)
        request.get_method = lambda: 'HEAD'
        response = urlopen(request, timeout=10)
        redirect_url = response.geturl()
        
        if redirect_url and not redirect_url.endswith("404"):
            return redirect_url
    except Exception:
        pass
    
    return url


def gaywire(obj, _):
    if obj is None:
        return None

    # API returns Gay Wire substudios as bangbros.com
    fixed = replace_all(
        obj,
        "url",
        lambda x: x.replace("www.bangbros.com", "gaywire.com"),
    )

    # Rename certain studios according to the map
    fixed = replace_at(
        fixed, "studio", "name", replacement=lambda x: studio_map.get(x, x)
    )

    fixed = replace_at(
        fixed, "studio", "parent", "name", replacement=lambda x: "Gay Wire"
    )

    return fixed


if __name__ == "__main__":
    domains = ["gaywire", "guyselector"]
    op, args = scraper_args()
    result = None

    if op in ["gallery-by-url", "gallery-by-fragment"] and args.get("url"):
        url = redirect(args["url"])
        result = gallery_from_url(url, postprocess=gaywire)
    elif op == "scene-by-url" and args.get("url"):
        url = redirect(args["url"])
        result = scene_from_url(url, postprocess=gaywire)
    elif op == "scene-by-name" and args.get("name"):
        result = scene_search(args["name"], search_domains=domains, postprocess=gaywire)
    elif op in ["scene-by-fragment", "scene-by-query-fragment"]:
        args = replace_all(args, "url", redirect)
        result = scene_from_fragment(
            args, search_domains=domains, postprocess=gaywire
        )
    elif op == "performer-by-url" and "url" in args:
        url = redirect(args["url"])
        result = performer_from_url(url, postprocess=gaywire)
    elif op == "performer-by-fragment":
        result = performer_from_fragment(args)
    elif op == "performer-by-name" and args.get("name"):
        result = performer_search(args["name"], search_domains=domains, postprocess=gaywire)
    elif op == "movie-by-url" and args.get("url"):
        url = redirect(args["url"])
        result = movie_from_url(url, postprocess=gaywire)
    else:
        log.error("Operation: {}, arguments: {}".format(op, json.dumps(args)))
        sys.exit(1)

    print(json.dumps(result))
