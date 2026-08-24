# JHNRD 公開MCP — 鍵なし・読み取り専用

**https://jhnrd-mcp.oga-surf-project.workers.dev**

このデータベースを、MCP と素の HTTP の両方で配ります。**鍵は要りません。書き込みの口はありません。**

```
POST /mcp    MCP (JSON-RPC 2.0 / Streamable HTTP)
             ※GET /mcp は 405。server→client から先に話しかけることが無いので、SSE の受け口は開けていない
GET  /       案内
GET  /status.json  /items  /items/<id>  /sources  /sources/<id>
     /search?q=  /unconfirmed  /conflicts  /gaps  /disclosure  /cite
```

## なぜ置くか

中身は CC BY 4.0 で公開しています。**ですが JSON を置いてあるだけでは、道具として使うたびに誰かがパーサを書くことになります。書くたびに、書いた人の解釈が混ざります。** ここで配れば、混ざるのは一箇所で済みます。

## 何をしないか

- **算定の可否を判定しません。** 「算定できます」「該当します」を返しません。**試験で機械的に確かめています**（`mcp_test.mjs` 場面4）。
- **どの応答にも**、版・「算定の可否は判定しない」・**利益相反の開示**が必ず付きます。11個の道具すべてについて試験で確かめています（場面3）。
- **鍵を持ちません。KV も D1 も繋ぎません。** 繋いだ瞬間に、預かるものが生まれます。

## 道具

| 道具 | 何を返すか |
| --- | --- |
| `jhnrd_status` | 版・項目数・出典の素性の内訳・未確認の数・未解決の食い違いの数 |
| `jhnrd_list_items` | 項目の一覧（保険別・種別・未確認のみで絞れる） |
| `jhnrd_get_item` | 項目1件の全部。**出典を素性(tier)と現行かどうかつきで解決して返す** |
| `jhnrd_search` | 横断検索。**見つからなければ「制度に無いことを意味しない」と断る** |
| `jhnrd_unconfirmed` | **原文で確認できていない要件と、その理由** |
| `jhnrd_conflicts` | 出典どうしの食い違い。**両方の言い分を残したまま** |
| `jhnrd_gaps` | 埋まっていないもの・**取りに行って取れなかった記録**・途中まで分かったこと |
| `jhnrd_get_source` | 出典1件の素性と、それを使っている項目 |
| `jhnrd_list_sources` | 出典の一覧。**現行版の数を分けて数える** |
| `jhnrd_disclosure` | **誰が作り、誰に養われているか** |
| `jhnrd_how_to_cite` | 引用の仕方（版を添えること） |

## 配るデータについて

worker は**実行時に外へ取りに行きません。** 配るのは `rules.data.js`（`data/rules_2024.json` からの生成物）です。

理由は、一度やらかしたからです。**raw.githubusercontent の縁に古い版が残り、内部の MCP が古い数字を配りました。** 同じリポジトリの中に写しを置けば、CDN の遅れは入りません。

写しである以上、黙って古くなるのが最大の危険なので、**ずれたら CI が赤になります**（`python3 tools/make_mcp_data.py --check`）。

## 動かす

```bash
node mcp/mcp_test.mjs          # 試験（網は要らない。72件）
cd mcp && npx wrangler deploy  # 必ず mcp/ の中で打つこと
```

## 繋ぐ

Claude Desktop / Claude Code などの MCP クライアントから:

```json
{
  "mcpServers": {
    "jhnrd": { "type": "http", "url": "https://jhnrd-mcp.oga-surf-project.workers.dev/mcp" }
  }
}
```

素の HTTP でも同じものが取れます。

```bash
curl https://jhnrd-mcp.oga-surf-project.workers.dev/status.json
curl "https://jhnrd-mcp.oga-surf-project.workers.dev/search?q=特別管理"
curl https://jhnrd-mcp.oga-surf-project.workers.dev/disclosure
```

## 公式のレジストリに載せる

`server.json` はリポジトリの根にあり、**中身は `status.json` から生成しています**（`tools/make_metadata.py`）。版番号もデータの版から機械的に作っています（seed 19 → `0.19.0`）。**版番号が二つに割れて、どちらが本当か分からなくなるのを避けるためです。**

```bash
# https://github.com/modelcontextprotocol/registry
mcp-publisher login github        # io.github.ogasurfproject-jpg/... の名乗りを認証する
mcp-publisher publish             # リポジトリ根の server.json を出す
```

---

**請求や届出の判断の前に、必ず原文を確認してください。** この口が言えるのは「この加算にはA・B・Cの要件があり、Cはまだ原文で確認できていない」までです。
