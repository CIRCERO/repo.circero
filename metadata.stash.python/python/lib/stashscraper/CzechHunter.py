import json
import sys

try:
    from ..py_common import log
    from ..py_common.util import dig, replace_all
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
    from py_common.util import dig, replace_all
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


def czechhunter(obj, _):
    replacement = None
    studio_name = dig(obj, "studio", "name")
    if studio_name == "Czech Hunter":
        replacement = "czechhunter.com"
    elif studio_name == "Debt Dandy":
        replacement = "debtdandy.com"
    elif studio_name == "Dirty Scout":
        replacement = "dirtyscout.com"
    else:
        # This will never be correct, but I don't see a better way to handle it
        replacement = "bigstr.com"

    # Replace the studio name in all URLs
    fixed = replace_all(obj, "url", lambda x: x.replace("bigstr.com", replacement))

    return fixed


if __name__ == "__main__":
    domains = [
        "czechhunter",
        "debtdandy",
        "dirtyscout",
    ]
    op, args = scraper_args()
    result = None

    if op in ["gallery-by-url", "gallery-by-fragment"] and args.get("url"):
        result = gallery_from_url(args["url"], postprocess=czechhunter)
    elif op == "scene-by-url" and args.get("url"):
        result = scene_from_url(args["url"], postprocess=czechhunter)
    elif op == "scene-by-name" and args.get("name"):
        result = scene_search(args["name"], search_domains=domains, postprocess=czechhunter)
    elif op in ["scene-by-fragment", "scene-by-query-fragment"]:
        result = scene_from_fragment(
            args, search_domains=domains, postprocess=czechhunter
        )
    elif op == "performer-by-url" and "url" in args:
        result = performer_from_url(args["url"], postprocess=czechhunter)
    elif op == "performer-by-fragment":
        result = performer_from_fragment(args)
    elif op == "performer-by-name" and args.get("name"):
        result = performer_search(
            args["name"], search_domains=domains, postprocess=czechhunter
        )
    elif op == "movie-by-url" and args.get("url"):
        result = movie_from_url(args["url"], postprocess=czechhunter)
    else:
        log.error("Operation: {}, arguments: {}".format(op, json.dumps(args)))
        sys.exit(1)

    print(json.dumps(result))
