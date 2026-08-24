# -*- coding: utf-8 -*-
"""live.yml の判定を、偽の本番相手に走らせて確かめる。網は要らない。

なぜ要るか (2026-08-24):
  live.yml は「押したのに配っていない」を見つけるための門で、1日1回しか走らない。
  1日1回しか走らない門が壊れていることは、壊れてから最大1日、誰にも分からない。
  しかも中身は YAML の中に埋まった python なので、誰も読み直さない。

  だから、その判定だけを取り出して、偽の本番を7通り与えて確かめる。
  ここは毎回の CI で走る。網に繋がない(偽の本番は urlopen を差し替えて作る)。

  特に確かめたいのは、「届かなかった」の二つの意味を取り違えていないことである。
    接続が立たない = 届いていない → 警告のみ。届かないことは、古いことの証拠にならない。
    HTTP の番号が返った = 届いている。向こうが答えた → 200 以外なら赤。

  最初の版はここを一括りにしていた。GitHub の走者から 403 が返っていたのに、
  それを「届かなかった」として毎日緑を出していた。門があると皆が思っている場所に、門が無い。

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


# 偽の本番。urlopen を差し替えて作る。網には繋がない。
#   MAP に載っていない道 → 接続が立たない(OSError)。届いていない。
#   200 以外 → urllib と同じく HTTPError を投げる。届いて、向こうが答えた。
HARNESS = """
import json, os, sys, urllib.error, urllib.request
os.environ["JHNRD_LIVE_RETRY_SLEEP"] = "0"
MAP = json.loads(%r)
class _R:
    def __init__(s, st, b): s.status = st; s._b = b
    def read(s): return s._b.encode("utf-8")
    def __enter__(s): return s
    def __exit__(s, *a): return False
class _Fp:
    def __init__(s, b): s._b = b
    def read(s): return s._b.encode("utf-8")
def _open(req, timeout=0):
    url = getattr(req, "full_url", req)
    key = url.split("workers.dev", 1)[1] if "workers.dev" in url else url
    if key not in MAP: raise OSError("connection refused " + key)
    st, body = MAP[key]
    if st != 200:
        raise urllib.error.HTTPError(url, st, "err", {}, _Fp(body))
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

    REG = "https://registry.modelcontextprotocol.io/v0/servers?search=jhnrd"
    server_json = json.load(io.open(os.path.join(ROOT, "server.json"), encoding="utf-8"))

    def _row(version, meta, is_latest):
        row = {"server": {
            "name": "io.github.ogasurfproject-jpg/jhnrd",
            "version": version,
            "_meta": {"io.modelcontextprotocol.registry/publisher-provided": meta},
        }}
        if is_latest is not None:
            row["_meta"] = {"io.modelcontextprotocol.registry/official":
                            {"status": "active", "isLatest": is_latest}}
        return row

    def reg(version=None, meta=None, is_latest=True):
        m = {"conflict_of_interest": "Conflict of interest: ...", "license": "CC-BY-4.0"}
        if meta is not None:
            m = meta
        return (200, json.dumps({"servers": [
            _row(version or server_json["version"], m, is_latest)]}, ensure_ascii=False))

    def reg_many(is_latest=True):
        """古い版が先に並んだ応答。実物の ?search= はこの形で返ってくる。

        2026-08-25: これが無かったので、最初の1件(=一番古い版)を掴む誤りに
          気づけなかった。版を上げるたびに本番が赤くなった。
        """
        m = {"conflict_of_interest": "Conflict of interest: ...", "license": "CC-BY-4.0"}
        return (200, json.dumps({"servers": [
            _row("0.19.0", {}, False if is_latest is not None else None),
            _row("0.19.1", {}, False if is_latest is not None else None),
            _row(server_json["version"], m, is_latest),
        ]}, ensure_ascii=False))

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
        ("接続が立たない → 緑(警告のみ)。届かないことは古いことの証拠にならない", {}, 0),
        # 2026-08-24: ここが無かったせいで、門は403を受け取りながら毎日緑を出していた。
        ("本番が 403 を返す(届いている・拒まれた) → 赤",
         {"/status.json": (403, "Forbidden"), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("本番が 500 を返す → 赤",
         {"/status.json": (500, "boom"), "/items": ok_items, "/mcp": (405, "{}")}, 1),
        ("/items だけ 403 → 赤",
         {"/status.json": live(), "/items": (403, "Forbidden"), "/mcp": (405, "{}")}, 1),
        ("GET /mcp が 404 → 警告だけで緑",
         {"/status.json": live(), "/items": ok_items, "/mcp": (404, "{}")}, 0),
        ("レジストリに載っている版が古い → 赤",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"),
          REG: reg(version="0.18.0")}, 1),
        # 2026-08-24: 最初の publish は _meta を丸ごと捨てられ、公開された名刺は {} だった。
        ("レジストリの名刺から利益相反が消えている → 赤",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"),
          REG: reg(meta={})}, 1),
        ("レジストリに載っていない → 赤",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"),
          REG: (200, json.dumps({"servers": []}))}, 1),
        ("レジストリに接続できない → 緑(警告のみ)",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}")}, 0),
        ("レジストリに載っていて名刺も揃っている → 緑",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"), REG: reg()}, 0),
        # 2026-08-25: レジストリは古い版を捨てない。?search= は全部の版を返し、
        #   最初に来るのは一番古い版だった。最初の1件を掴んでいたので、
        #   版を上げて publish するたびに、この門が「版が違う」と言って赤くなった。
        ("古い版も一緒に並んで返ってくる → 最新版を見て緑",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"),
          REG: reg_many()}, 0),
        ("どの版にも isLatest が無い → 版の大きいものを見て緑(警告のみ)",
         {"/status.json": live(), "/items": ok_items, "/mcp": (405, "{}"),
          REG: reg_many(is_latest=None)}, 0),
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

    EXPECT = 19  # 場面を足したら、ここも直すこと。数が合わないこと自体を赤にする。
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
