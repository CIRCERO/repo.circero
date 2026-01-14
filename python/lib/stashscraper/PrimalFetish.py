import json

try:
    from ..py_common import log
    from ..py_common.util import replace_at
    from ..AyloAPI.scrape import (
        gallery_from_url,
        gallery_from_fragment,
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
    # Fallback for direct execution
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from py_common import log
    from py_common.util import replace_at
    from AyloAPI.scrape import (
        gallery_from_url,
        gallery_from_fragment,
        scraper_args,
        scene_from_url,
        scene_search,
        scene_from_fragment,
        performer_from_url,
        performer_from_fragment,
        performer_search,
        movie_from_url,
    )


def primalfetish(obj, _):
    """
    Post-process Primal Fetish Network scenes
    Handles URL formatting and studio naming
    """
    # Primal Fetish Network uses standard /scene/ URLs
    # No special URL transformations needed
    
    # Set the parent studio to Primal Fetish Network
    fixed = replace_at(
        obj, "studio", "parent", replacement=lambda _: {"name": "Primal Fetish Network"}
    )
    
    return fixed


if __name__ == "__main__":
    domains = [
        "primalfetish",
        "primalfetishnetwork"
    ]
    op, args = scraper_args()
    result = None

    if op == "gallery-by-url" and args.get("url"):
        result = gallery_from_url(args["url"], postprocess=primalfetish)
    elif op == "gallery-by-fragment":
        result = gallery_from_fragment(
            args, search_domains=domains, postprocess=primalfetish
        )
    elif op == "scene-by-url" and args.get("url"):
        result = scene_from_url(args["url"], postprocess=primalfetish)
    elif op == "scene-by-name" and args.get("name"):
        result = scene_search(args["name"], search_domains=domains, postprocess=primalfetish)
    elif op in ["scene-by-fragment", "scene-by-query-fragment"]:
        result = scene_from_fragment(
            args, search_domains=domains, postprocess=primalfetish
        )
    elif op == "performer-by-url" and "url" in args:
        result = performer_from_url(args["url"], postprocess=primalfetish)
    elif op == "performer-by-fragment":
        result = performer_from_fragment(args)
    elif op == "performer-by-name" and args.get("name"):
        result = performer_search(
            args["name"], search_domains=domains, postprocess=primalfetish
        )
    elif op == "movie-by-url" and args.get("url"):
        result = movie_from_url(args["url"], postprocess=primalfetish)
    else:
        log.error("Operation: {}, arguments: {}".format(op, json.dumps(args)))
        sys.exit(1)

    print(json.dumps(result))
