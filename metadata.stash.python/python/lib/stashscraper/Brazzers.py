import json

try:
    from ..py_common import log
    from ..py_common.util import dig, replace_all, replace_at
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
    from py_common.util import dig, replace_all, replace_at
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

studio_map = {
    "JugFuckers": "Jug Fuckers",
    "Shes Gonna Squirt": "She's Gonna Squirt",
}


def brazzers(obj, _):
    # All brazzers URLs use /video/ instead of the standard /scene/
    # and /pornstar/ instead of the standard /model
    fixed = replace_all(
        obj,
        "url",
        lambda x: x.replace("/scene/", "/video/").replace("/model/", "/pornstar/"),
    )

    # Rename certain studios according to the map
    fixed = replace_at(
        fixed, "studio", "name", replacement=lambda x: studio_map.get(x, x)
    )

    # Brazzers Live special case: if the scene has the tag "Brazzers Live" we need to set the studio name to "Brazzers Live"
    if any(t["name"] == "Brazzers Live" for t in dig(obj, "tags", default=[])):
        fixed = replace_at(
            fixed, "studio", "name", replacement=lambda _: "Brazzers Live"
        )

    return fixed


if __name__ == "__main__":
    domains = [
        "brazzers",
    ]
    op, args = scraper_args()
    result = None

    if op == "gallery-by-url" and args.get("url"):
        result = gallery_from_url(args["url"], postprocess=brazzers)
    elif op == "gallery-by-fragment":
        result = gallery_from_fragment(
            args, search_domains=domains, postprocess=brazzers
        )
    elif op == "scene-by-url" and args.get("url"):
        result = scene_from_url(args["url"], postprocess=brazzers)
    elif op == "scene-by-name" and args.get("name"):
        result = scene_search(args["name"], search_domains=domains, postprocess=brazzers)
    elif op in ["scene-by-fragment", "scene-by-query-fragment"]:
        result = scene_from_fragment(
            args, search_domains=domains, postprocess=brazzers
        )
    elif op == "performer-by-url" and "url" in args:
        result = performer_from_url(args["url"], postprocess=brazzers)
    elif op == "performer-by-fragment":
        result = performer_from_fragment(args)
    elif op == "performer-by-name" and args.get("name"):
        result = performer_search(
            args["name"], search_domains=domains, postprocess=brazzers
        )
    elif op == "movie-by-url" and args.get("url"):
        result = movie_from_url(args["url"], postprocess=brazzers)
    else:
        log.error("Operation: {}, arguments: {}".format(op, json.dumps(args)))
        sys.exit(1)

    print(json.dumps(result))
