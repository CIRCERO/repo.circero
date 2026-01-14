# -*- coding: utf-8 -*-
"""
AEBN Scraper (AEBN VOD / Straight site style)
- Uses cookie-based session (urllib opener + cookiejar)
- Login endpoint aligns with devtools: /straight/login-action
- Search endpoint aligns with devtools: /search/scenes/page/1?...criteria=...
- Works even when pages are HTML (extracts JSON blobs if present, otherwise scrapes links/meta)
Compatible with Python 2.7+ and Python 3.x (Kodi environments)
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import re
import ssl

try:
    import xbmc  # Kodi
except Exception:
    xbmc = None

try:
    # Py2
    from urllib import urlencode
    from urlparse import urljoin
    import cookielib as cookiejar
    from urllib2 import (
        Request,
        build_opener,
        HTTPCookieProcessor,
        HTTPSHandler,
        HTTPError,
        URLError,
    )
except ImportError:
    # Py3
    from urllib.parse import urlencode, urljoin
    import http.cookiejar as cookiejar
    from urllib.request import (
        Request,
        build_opener,
        HTTPCookieProcessor,
        HTTPSHandler,
    )
    from urllib.error import HTTPError, URLError


def _log(msg, level="INFO"):
    try:
        if xbmc:
            lvl = xbmc.LOGINFO
            if level == "ERROR":
                lvl = xbmc.LOGERROR
            elif level == "WARNING":
                lvl = xbmc.LOGWARNING
            xbmc.log("[AEBN] %s" % msg, lvl)
        else:
            print("[AEBN][%s] %s" % (level, msg))
    except Exception:
        pass


class AEBNScraper(object):
    """
    Scraper for AEBN (Straight site style endpoints)
    """

    def __init__(self, aebn_url, username=None, password=None, debug=False, timeout=30):
        self.base = (aebn_url or "").rstrip("/")  # e.g. https://straight.aebn.com or https://www.aebn.com
        self.username = username or ""
        self.password = password or ""
        self.debug = bool(debug)
        self.timeout = int(timeout)

        # SSL context (Kodi boxes sometimes have weird cert stores)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        self.cj = cookiejar.CookieJar()
        self.opener = build_opener(
            HTTPCookieProcessor(self.cj),
            HTTPSHandler(context=self.ssl_context),
        )

        self._is_logged_in = False

        # A sane default UA (some sites behave differently without one)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )

    # ----------------------------
    # Core HTTP helpers
    # ----------------------------
    def _headers(self, extra=None):
        h = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        if extra:
            h.update(extra)
        return h

    def _request(self, method, path_or_url, params=None, data=None, headers=None, allow_redirects=True):
        """
        Returns: (status_code, final_url, body_bytes, content_type)
        """
        url = path_or_url
        if not re.match(r"^https?://", url, re.I):
            url = urljoin(self.base + "/", path_or_url.lstrip("/"))

        if params:
            qs = urlencode(params)
            url = url + ("&" if "?" in url else "?") + qs

        body = None
        if data is not None:
            # form-encoded POST by default
            if isinstance(data, dict):
                body = urlencode(data).encode("utf-8")
            else:
                body = data
            if headers is None:
                headers = {}
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")

        req = Request(url, data=body)
        for k, v in self._headers(headers).items():
            try:
                req.add_header(k, v)
            except Exception:
                pass

        if self.debug:
            _log("%s %s" % (method.upper(), url))
            if body and self.debug:
                _log("POST body: %s" % (body[:300] if isinstance(body, (bytes, bytearray)) else str(body)[:300]))

        try:
            resp = self.opener.open(req, timeout=self.timeout)
            final_url = getattr(resp, "geturl", lambda: url)()
            code = getattr(resp, "getcode", lambda: 200)()
            info = getattr(resp, "info", lambda: {})()
            ctype = ""
            try:
                ctype = info.get("Content-Type", "") or info.getheader("Content-Type") or ""
            except Exception:
                pass

            raw = resp.read()
            return code, final_url, raw, ctype

        except HTTPError as e:
            try:
                raw = e.read()
            except Exception:
                raw = b""
            ctype = ""
            try:
                ctype = e.headers.get("Content-Type", "")
            except Exception:
                pass
            if self.debug:
                _log("HTTPError %s for %s" % (getattr(e, "code", "???"), url), "WARNING")
            return getattr(e, "code", 0), url, raw, ctype
        except URLError as e:
            if self.debug:
                _log("URLError for %s: %s" % (url, e), "ERROR")
            return 0, url, b"", ""

    def _decode(self, b):
        if b is None:
            return ""
        if isinstance(b, str):
            return b
        # bytes -> str
        for enc in ("utf-8", "windows-1252", "latin-1"):
            try:
                return b.decode(enc)
            except Exception:
                continue
        try:
            return b.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    # ----------------------------
    # JSON / HTML extraction helpers
    # ----------------------------
    def _extract_json_blobs(self, html_text):
        """
        Tries to extract JSON objects/arrays embedded in HTML/JS.
        Returns list of parsed python objects.
        """
        out = []

        # Common patterns: window.__INITIAL_STATE__ = {...};
        #                  __NEXT_DATA__ = {...}
        patterns = [
            r"__NEXT_DATA__\s*=\s*({.*?})\s*;?</script>",
            r"__NUXT__\s*=\s*({.*?})\s*;?</script>",
            r"window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;?",
            r"window\.__STATE__\s*=\s*({.*?})\s*;?",
        ]

        for pat in patterns:
            for m in re.finditer(pat, html_text, flags=re.S | re.I):
                blob = m.group(1)
                try:
                    out.append(json.loads(blob))
                except Exception:
                    continue

        # Generic: look for {"results":[...]} or {"data":[...]} blobs
        for pat in [
            r"(\{\s*\"results\"\s*:\s*\[.*?\]\s*.*?\})",
            r"(\{\s*\"data\"\s*:\s*\[.*?\]\s*.*?\})",
        ]:
            for m in re.finditer(pat, html_text, flags=re.S):
                blob = m.group(1)
                try:
                    out.append(json.loads(blob))
                except Exception:
                    continue

        return out

    def _find_meta(self, html_text, prop):
        """
        Extracts meta property or name content.
        """
        # og:title etc
        m = re.search(
            r'<meta[^>]+(?:property|name)\s*=\s*["\']%s["\'][^>]+content\s*=\s*["\']([^"\']+)["\']' % re.escape(prop),
            html_text,
            flags=re.I,
        )
        return m.group(1).strip() if m else ""

    def _scrape_content_links(self, html_text):
        """
        Finds /content/... links in search pages.
        Returns list of dicts with id,url,title.
        """
        items = []
        # /content/12345 or /content/slug/12345 etc
        for m in re.finditer(r'href=["\'](/content/[^"\']+)["\']', html_text, flags=re.I):
            href = m.group(1)
            # try to find an id at the end
            idm = re.search(r"(\d+)(?:\D*$)", href)
            scene_id = idm.group(1) if idm else href
            items.append({"id": str(scene_id), "url": href, "title": ""})

        # Attempt to pull nearby text title (very heuristic)
        # (kept simple for stability)
        dedup = []
        seen = set()
        for it in items:
            key = it["url"]
            if key in seen:
                continue
            seen.add(key)
            dedup.append(it)
        return dedup

    # ----------------------------
    # Auth
    # ----------------------------
    def login(self):
        """
        Attempt login via /straight/login-action.
        Many accounts may require captcha; if so, login may fail and we proceed anonymously.
        """
        if not (self.username and self.password):
            self._is_logged_in = False
            return False

        # Best-effort: send username/password as form fields.
        # Field names can vary; we try a few common ones.
        action = "/straight/login-action"

        field_sets = [
            {"username": self.username, "password": self.password},
            {"userName": self.username, "password": self.password},
            {"loginFormUsername": self.username, "loginFormPassword": self.password},
            {"email": self.username, "password": self.password},
        ]

        for fields in field_sets:
            code, final_url, raw, ctype = self._request("POST", action, data=fields, headers={"Referer": urljoin(self.base + "/", "/login")})
            txt = self._decode(raw)

            if self.debug:
                _log("Login attempt code=%s final=%s ctype=%s cookies=%s" % (code, final_url, ctype, len(list(self.cj))))

            # If we land on something not containing "Login" forms, assume ok.
            if code in (200, 302, 301) and ("login" not in final_url.lower()) and len(list(self.cj)) > 0:
                self._is_logged_in = True
                return True

            # Sometimes it stays 200 but sets cookies; also look for obvious failure strings
            if len(list(self.cj)) > 0 and not re.search(r"(invalid|incorrect|failed|captcha)", txt, re.I):
                # still might be ok
                self._is_logged_in = True
                return True

        self._is_logged_in = False
        return False

    # ----------------------------
    # Public API expected by scrapers
    # ----------------------------
    def search(self, title, year=None, limit=20):
        """
        Searches scenes using /search/scenes/page/1 endpoint.

        Devtools shows patterns like:
          /search/scenes/page/1?queryType=Free+Form&query=PLACEHOLDER&criteria={"sort":"Relevance"}
        """
        if not title:
            return []

        # Ensure we tried login once (optional)
        if not self._is_logged_in and self.username and self.password:
            self.login()

        criteria = {"sort": "Relevance"}
        params = {
            "queryType": "Free Form",
            "query": title,
            "criteria": json.dumps(criteria),
        }

        code, _, raw, ctype = self._request("GET", "/search/scenes/page/1", params=params, headers={"Referer": urljoin(self.base + "/", "/search")})
        html = self._decode(raw)

        if self.debug:
            _log("Search response code=%s ctype=%s bytes=%s" % (code, ctype, len(raw or b"")))

        scenes = []

        # 1) Try JSON blobs
        blobs = self._extract_json_blobs(html)
        for obj in blobs:
            # Find list-like candidates
            for key in ("results", "data", "items"):
                arr = obj.get(key) if isinstance(obj, dict) else None
                if isinstance(arr, list):
                    for it in arr:
                        sid = it.get("id") or it.get("sceneId") or it.get("contentId") or ""
                        stitle = it.get("title") or it.get("name") or ""
                        sdate = it.get("release_date") or it.get("releaseDate") or it.get("date") or ""
                        img = it.get("thumbnail") or it.get("image") or it.get("poster") or ""
                        if sid or stitle:
                            scenes.append({
                                "id": str(sid) if sid else stitle,
                                "title": stitle or title,
                                "date": sdate,
                                "image": img,
                                "studio": "",
                                "performers": [],
                                "url": it.get("url") or "",
                            })

        # 2) Fallback: scrape /content/... links from HTML
        if not scenes:
            links = self._scrape_content_links(html)
            for it in links[: max(5, int(limit))]:
                scenes.append({
                    "id": it["id"],
                    "title": it.get("title") or title,
                    "date": "",
                    "image": "",
                    "studio": "",
                    "performers": [],
                    "url": it.get("url") or "",
                })

        # Optional: crude year filter if provided
        if year:
            y = str(year)
            scenes = [s for s in scenes if (y in (s.get("date") or "")) or not s.get("date")]

        return scenes[: int(limit)]

    def get_details(self, scene_id_or_path):
        """
        Fetches a /content/... page and returns:
          {'info': ..., 'cast': ..., 'uniqueids': ..., 'available_art': ...}
        """
        if not scene_id_or_path:
            return {"error": "Scene id/path missing"}

        # If caller passed numeric id only, map to /content/<id>
        path = str(scene_id_or_path).strip()
        if re.match(r"^\d+$", path):
            path = "/content/%s" % path
        elif not path.startswith("/"):
            # might be a full URL or a slug path
            if re.match(r"^https?://", path, re.I):
                # full URL ok
                pass
            else:
                path = "/" + path

        if not self._is_logged_in and self.username and self.password:
            self.login()

        code, final_url, raw, ctype = self._request("GET", path, headers={"Referer": urljoin(self.base + "/", "/search")})
        html = self._decode(raw)

        if self.debug:
            _log("Details code=%s url=%s ctype=%s" % (code, final_url, ctype))

        # Pull from meta first (usually present)
        title = self._find_meta(html, "og:title") or self._find_meta(html, "twitter:title") or ""
        image = self._find_meta(html, "og:image") or self._find_meta(html, "twitter:image") or ""
        desc = self._find_meta(html, "og:description") or self._find_meta(html, "description") or ""

        # Try to find release date in obvious places
        premiered = ""
        m = re.search(r"(Release Date|Released)\s*[:\-]?\s*</?[^>]*>\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}|\d{4}-\d{2}-\d{2})", html, re.I)
        if m:
            premiered = m.group(2).strip()

        # Try to extract performers (heuristic)
        performers = []
        for pm in re.finditer(r'/search/stars/page/\d+\?[^"\']*["\'][^>]*>\s*([^<]{2,80})\s*<', html, re.I):
            name = pm.group(1).strip()
            if name and name.lower() not in ("stars", "models"):
                performers.append(name)
        performers = list(dict.fromkeys(performers))  # dedupe keep order

        # Try to parse any embedded JSON blobs for richer fields
        blobs = self._extract_json_blobs(html)
        duration = None
        rating = None
        studio = ""
        tags = []
        genres = []
        cast = []

        for obj in blobs:
            # Try to find "content" dicts
            if isinstance(obj, dict):
                candidate = obj.get("content") or obj.get("scene") or obj.get("data") or obj
                if isinstance(candidate, dict):
                    title = title or candidate.get("title") or candidate.get("name") or ""
                    desc = desc or candidate.get("description") or candidate.get("synopsis") or ""
                    image = image or candidate.get("image") or candidate.get("poster") or candidate.get("thumbnail") or ""

                    studio = studio or (candidate.get("studio") if isinstance(candidate.get("studio"), str) else "")
                    duration = duration or candidate.get("duration") or candidate.get("runtime")
                    rating = rating or candidate.get("rating")

                    for key in ("tags", "categories", "genres"):
                        arr = candidate.get(key)
                        if isinstance(arr, list):
                            for t in arr:
                                if isinstance(t, dict):
                                    nm = t.get("name") or ""
                                else:
                                    nm = str(t)
                                nm = nm.strip()
                                if nm:
                                    tags.append(nm)

                    # performers in json
                    parr = candidate.get("performers") or candidate.get("models") or candidate.get("stars")
                    if isinstance(parr, list) and not performers:
                        for p in parr:
                            if isinstance(p, dict):
                                nm = p.get("name") or ""
                                imgp = p.get("image") or p.get("thumbnail") or ""
                            else:
                                nm = str(p)
                                imgp = ""
                            nm = (nm or "").strip()
                            if nm:
                                performers.append(nm)
                                cast.append({"name": nm, "role": "", "order": len(cast), "thumbnail": imgp})

        # Build cast if not already
        if not cast and performers:
            for i, nm in enumerate(performers):
                cast.append({"name": nm, "role": "", "order": i, "thumbnail": ""})

        # Normalize duration
        if duration is not None:
            try:
                d = float(duration)
                # if minutes, convert to seconds
                if d < 500:
                    d = d * 60.0
                duration = int(d)
            except Exception:
                duration = None

        # Minimal fallback if title still empty
        if not title:
            # try <title> tag
            mt = re.search(r"<title>\s*([^<]+)\s*</title>", html, re.I)
            if mt:
                title = mt.group(1).strip()

        info = {
            "title": title or "Untitled",
            "originaltitle": title or "Untitled",
            "plot": desc or "",
            "tagline": final_url or "",
            "studio": [studio] if studio else [],
            "genre": genres,
            "tag": list(dict.fromkeys(tags)),
            "director": [],
            "premiered": premiered or "",
        }
        if duration:
            info["duration"] = duration
        if rating is not None:
            try:
                info["rating"] = float(rating)
            except Exception:
                pass

        available_art = {}
        if image:
            available_art["poster"] = [{"url": image, "preview": image}]
            available_art["thumb"] = [{"url": image, "preview": image}]
            available_art["fanart"] = [{"url": image, "preview": image}]

        # Unique id: use numeric if possible
        uid = ""
        if re.match(r"^\d+$", str(scene_id_or_path).strip()):
            uid = str(scene_id_or_path).strip()
        else:
            m = re.search(r"/content/(\d+)", final_url or "", re.I)
            uid = m.group(1) if m else str(scene_id_or_path)

        return {
            "info": info,
            "cast": cast,
            "uniqueids": {"aebn": uid},
            "available_art": available_art,
        }
