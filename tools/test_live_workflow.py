# -*- coding: utf-8 -*-
"""live.yml の判定を、偽の本番相手に走らせて確かめる。網は要らない。

なぜ要るか (2026-08-24):
  live.yml は「押したのに配っていない」を見つけるための門で、1日1回しか走らない。
  1日1回しか走らない門が壊れていることは、壊れてから最大1日、誰にも分からない。
  しかも中身は YAML の中に埋まった python なので、誰も読み直さない。

  だから、その判定だけを取り出して、偽の本番を7通り与えて確かめる。
  ここは毎回の CI で走る。網に繋がない(偽の本番は urlopen を差し替えて作る)。

  特に確かめたいのは「届かないとき赤にしない」ことである。
  届かないことは、古いことの証拠にならない。
  そこを赤にすると、向こうの都合でこちらが赤くなり、赤が普通になって門が門でなくなる。

使い方:
  python3 tools/test_live_workflow.py
"""
import io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "live.yml")
STATUS = os.path.join(ROOT, "status.json")


def extract():
    y = io.open(WORKFLOW, encoding="utf-8").read()
    m = re.search(r"python3 - <<'PY'\n(.*?)\n\s*PY\n", y, re.S)
    if not m:
        sys.exit("live.yml から判定の本体を取り出せませんでした。")
    body = m.group(1)
    indent = min(len(l) - len(l.lstrip()) for l in body.split("\n") if l.strip())
    return "\n".join(l[indent:] if len(l) >= indent else l for l in body.split("\n"))


HARNESS = """
import json, sys, urllib.request
MAP = json.loads(%r)
class _R:
    def __init__(s, st, b): s.status = st; s._b = b
    def read(s): return s._b.encode("utf-8")
    def __enter__(s): return s
    def __exit__(s, *a): return False
def _open(url, timeout=0):
    p = url.split("workers.dev", 1)[1]
    if p not in MAP: raise OSError("unreachable " + p)
    st, body = MAP[p]
    return _R(st, body)
urllib.request.urlopen = _open
"""


def main():
    src = extract()
    want = json.load(io.open(STATUS, encoding="utf-8"))

    def live(**over):
        d = {
            "version": want["version"], "items": want["items"],
            "unconfirmed_requirements": want["unconfirmed_requirements"],
            "open_conflicts": want["open_conflicts"],
            "statute_current": want["statute_current"],
            "disclosure": "利益相反: ...有償のサービス...",
            "we_do_not_say": "算定の可否は判定しない。...",
        }
        d.update(over)
        return (200, json.dumps(d, ensure_ascii=False))

    ok_items = (200, json.dumps(
        {"count": 1, "items": [{"id": "x"}],
         "we_do_not_say": "『算定できます』『該当します』とは返さない。"}, ensure_ascii=False))
    bad_items = (200, json.dumps(
        {"count": 1, "items": [{"id": "x", "note": "この加算は算定できます"}],
         "we_do_not_say": "『算定できます』『該当します』とは返さない。"}, ensure_ascii=False))

    cases = [
        ("本番とリポジトリが一致 → 緑",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}")}, 0),
        ("配っている版が古い → 赤",
         {"/status.json": live(version="2024-kaitei.seed.18"), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("項目数が違う → 赤",
         {"/status.json": live(items=8), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("未確認の件数が違う → 赤",
         {"/status.json": live(unconfirmed_requirements=0), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("開示が応答から消えた → 赤",
         {"/status.json": live(disclosure=""), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("断り書きが応答から消えた → 赤",
         {"/status.json": live(we_do_not_say=""), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("本番が断定を返した → 赤",
         {"/status.json": live(), "/items": bad_items, "/mcp": (405, "{}")}, 1),
        ("本番に届かない → 緑(警告のみ)。届かないことは古いことの証拠にならない", {}, 0),
        ("GET /mcp が 404 → 警告だけで緑",
         {"/status.json": live(), "/items": ok_items, "/mcp": (404, "{}")}, 0),
    ]

    fail, ran = 0, 0
    print("live.yml の判定（偽の本番・網なし）")
    for label, mapping, expect in cases:
        p = subprocess.run([sys.executable, "-c", (HARNESS % json.dumps(mapping)) + src],
                           capture_output=True, text=True, cwd=ROOT)
        good = p.returncode == expect
        ran += 1
        print(("  ok   " if good else "  NG   ") + label + "  (exit=%d / 期待 %d)" % (p.returncode, expect))
        if not good:
            fail += 1
            print("       " + ((p.stdout or "") + (p.stderr or "")).strip()[:400].replace("\n", "\n       "))

    EXPECT = 9  # 場面を足したら、ここも直すこと。数が合わないこと自体を赤にする。
    print("")
    print("確かめた数: %d 件" % ran)
    if ran != EXPECT:
        print("確かめた数が %d と合わない。場面を足して EXPECT を直していない。" % EXPECT)
        return 1
    if fail:
        print("%d 件おかしい。" % fail)
        return 1
    print("live.yml の判定 すべて通過 (%d 件)" % ran)
    return 0


if __name__ == "__main__":
    sys.exit(main())
