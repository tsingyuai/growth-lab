# Xiaohongshu configuration map

Inspect the installed commit before use. Current upstream uses `XHS_SPECIFIED_NOTE_URL_LIST` for detail links and `XHS_CREATOR_ID_LIST` for creators in `config/xhs_config.py`. Search keywords and shared limits live in `config/base_config.py`.

Exact detail links must retain anti-abuse query parameters supplied by the platform, especially `xsec_token`; `xsec_source` is normally also required. A bare note ID is not equivalent to a working browser link.

MediaCrawler can enrich a known link with note detail, configured comments, and images/video in one detail run. This is the standard route; XHS-Downloader is no longer a Growth Lab dependency.
