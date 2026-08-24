# -*- coding: utf-8 -*-
"""
公開MCPが配るデータを、data/rules_2024.json と status.json から書き起こす。

なぜ写しを置くか (2026-08-24):
  worker が実行時に raw.githubusercontent から取りに行く形にすると、
  CDN の縁で古い版が数分〜数十分残る。それで一度、内部MCPが古い数字を配った。
  だから写しを同じリポジトリの中に置いて、ずれていたら CI で止める。
  同じリポジトリの中なので、CDN の遅れは入らない。

  写しである以上、黙って古くなるのが最大の危険なので、
  --check を CI に入れてある。写しが本体とずれたら赤になる。

使い方:
  python3 tools/make_mcp_data.py --write
  python3 tools/make_mcp_data.py --check
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RULES = os.path.join(ROOT, "data", "rules_2024.json")
STATUS = os.path.join(ROOT, "status.json")
OUT = os.path.join(ROOT, "mcp", "rules.data.js")

HEAD = """// 自動生成。手で書かない。
//   python3 tools/make_mcp_data.py --write
// 出どころ: data/rules_2024.json / status.json
// ずれていたら CI が赤になる (python3 tools/make_mcp_data.py --check)
//
// 版: %s
// 項目 %d / 出典 %d / 未確認の要件 %d / 未解決の食い違い %d
"""


def js(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    # JSON では素通りするが JavaScript の文字列では行終端に化ける2文字を潰す。
    return s.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def build():
    db = json.load(io.open(RULES, encoding="utf-8"))
    st = json.load(io.open(STATUS, encoding="utf-8"))
    head = HEAD % (db["version"], len(db["items"]), len(db["sources"]),
                   st.get("unconfirmed_requirements", 0), st.get("open_conflicts", 0))
    return (head +
            "\nexport const DB = " + js(db) + ";\n" +
            "\nexport const STATUS = " + js(st) + ";\n" +
            "\nexport default { DB, STATUS };\n")


def main():
    want = build()
    cur = io.open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
    if cur == want:
        print("mcp/rules.data.js は data/rules_2024.json と一致しています。")
        return 0
    if "--write" in sys.argv:
        io.open(OUT, "w", encoding="utf-8").write(want)
        print("書き直しました: mcp/rules.data.js")
        return 0
    print("mcp/rules.data.js が本体とずれています。")
    print("  python3 tools/make_mcp_data.py --write  で直せます。")
    return 1 if "--check" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
