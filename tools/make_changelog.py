# -*- coding: utf-8 -*-
"""
版ごとの記録(CHANGELOG.md)を、annotated tag から書き起こす。

なぜ要る (2026-08-24):
  「訂正しても元の記述を消さない」と言っている以上、
  どの版で何をどう直したかが、外から一覧で読めなければ意味がない。
  tag の注釈にはそれが書いてあるのに、リポジトリを clone しないと読めなかった。

  なお、これは CI で突き合わせない。
  版を切る commit は、その版の tag より必ず先に存在するので、
  「CHANGELOG が最新の tag を含んでいること」を機械に要求すると、必ず落ちるからである。
  代わりに、次に版を切るときに一緒に打ち直す。

使い方:
  python3 tools/make_changelog.py --write
"""
import io, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "CHANGELOG.md")

HEAD = """# 版ごとの記録

**版が違えば中身が違います。** 引用するときは版（seed 番号）を添えてください。

訂正しても元の記述は消しません（[GOVERNANCE.md](GOVERNANCE.md) 4）。
つまり**過去の誤りは、消えずに、訂正として積まれています。** 下はその積まれ方の一覧です。

この文書は `python3 tools/make_changelog.py --write` で annotated tag から生成しています。
手で書き足さないでください。版の記録は tag の注釈が正です。

---
"""


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def seedno(t):
    """seed.19 と seed.19.1 の両方を受ける。

    2026-08-24: データの版(seed)が動かないまま、周りだけが変わることがある。
      公開MCP・利益相反の開示・レジストリの名刺など。
      そのとき seed を上げるのは嘘になる(中身は同じなので)が、
      Zenodo の Release は切りたい。だから seed.19.1 の形を足した。
      数え方は (seed, 枝番)。枝番が無ければ 0。
      正規表現を $ で締めていたので、足す前は seed.19.1 が黙って一覧から落ちていた。
      黙って落ちるのが一番よくないので、ここに書いておく。
    """
    m = re.search(r"seed\.(\d+)(?:\.(\d+))?$", t)
    if not m:
        return (-1, -1)
    return (int(m.group(1)), int(m.group(2) or 0))


def main():
    tags = [t for t in git("tag", "-l", "seed.*").split() if seedno(t)[0] >= 0]
    tags.sort(key=seedno, reverse=True)
    if not tags:
        sys.exit("seed.* の tag がありません。")

    parts = [HEAD]
    for t in tags:
        date = git("log", "-1", "--format=%ad", "--date=short", t).strip()
        body = git("tag", "-l", "--format=%(contents)", t).strip()
        subject = git("log", "-1", "--format=%h", t).strip()
        parts.append("\n## `%s` — %s\n\n%s\n\n<sub>commit `%s` ・ `git show %s`</sub>\n"
                     % (t, date, body if body else "（注釈なし）", subject, t))

    have = set(seedno(t)[0] for t in tags)
    missing = [n for n in range(1, seedno(tags[0])[0] + 1) if n not in have]
    if missing:
        parts.append("\n---\n\n<sub>seed.%s は、その番号で commit された状態が存在しないため "
                     "tag がありません（版を切らずに番号だけ進んだもの）。"
                     "欠番も、あったことにはしません。</sub>\n"
                     % "・seed.".join(str(m) for m in missing))

    io.open(OUT, "w", encoding="utf-8").write("".join(parts))
    print("CHANGELOG.md を書き直しました（%d 版）。" % len(tags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
