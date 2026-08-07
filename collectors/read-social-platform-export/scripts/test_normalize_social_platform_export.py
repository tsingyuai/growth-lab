from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("normalize_social_platform_export.py")


def test_normalize_chinese_social_export(tmp_path: Path) -> None:
    export = tmp_path / "xhs.csv"
    export.write_text(
        "\n".join(
            [
                "日期,笔记ID,标题,曝光,浏览,点赞,评论,收藏,分享,新增关注,链接点击",
                "2026-07-28,note-1,文献综述怎么写,1000,200,20,5,30,2,3,8",
                "2026-07-29,note-1,文献综述怎么写,500,100,10,1,15,1,1,4",
                "bad-date,note-2,AI 痕迹怎么改,300,90,9,2,6,1,0,2",
                "2026-07-29,,缺少 ID,100,10,1,0,0,0,0,0",
            ]
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(export), "--platform", "xiaohongshu"],
        check=True,
        text=True,
        capture_output=True,
    )
    result = json.loads(completed.stdout)

    assert result["platform"] == "xiaohongshu"
    assert result["quality"]["input_rows"] == 4
    assert result["quality"]["usable_rows"] == 2
    assert result["quality"]["missing_post"] == 1
    assert result["quality"]["invalid_values"] == 1
    assert result["quality"]["unique_posts"] == 1
    assert result["totals"]["impressions"] == 1500
    assert result["totals"]["views"] == 300
    assert result["totals"]["engagements"] == 84
    assert result["totals"]["view_rate"] == 0.2
    assert result["totals"]["click_rate_by_view"] == 0.04
    assert result["posts"][0]["post"] == "note-1"
