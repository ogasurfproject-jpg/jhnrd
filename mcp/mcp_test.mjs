// 公開MCPの試験。網は要らない。node mcp/mcp_test.mjs で走る。
//
// 走らなかった試験は、通った試験と見分けがつかない。
// 別のリポジトリで、途中の process.exit のせいで最後の場面が一度も走らず、
// それでも「すべて通過」と出ていたことがある。
// だから、おかしかった数だけでなく、確かめた数も数えて、合わなければ赤にする。

import { handle, handleRpc, callTool, TOOLS } from "./worker.js";
import { DB, STATUS } from "./rules.data.js";

let fail = 0, ran = 0;
function check(label, cond, detail) {
  console.log((cond ? "  ok   " : "  NG   ") + label + (detail ? "  " + detail : ""));
  ran++;
  if (!cond) fail++;
}

const rpc = (method, params, id) =>
  handleRpc({ jsonrpc: "2.0", id: id === undefined ? 1 : id, method, params });

const call = (name, args) => callTool(name, args || {});

async function http(method, path, body) {
  const req = new Request("https://example.invalid" + path, {
    method,
    headers: body ? { "content-type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const res = await handle(req);
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch (_e) {}
  return { status: res.status, text, json, res };
}

console.log("\n1) 名乗り");
{
  const r = rpc("initialize", { protocolVersion: "2024-11-05" });
  check("initialize が返る", !!r.result);
  check("相手が名乗った版をそのまま返す", r.result.protocolVersion === "2024-11-05", r.result.protocolVersion);
  check("知らない版なら既定に落とす",
        rpc("initialize", { protocolVersion: "1999-01-01" }).result.protocolVersion === "2025-06-18");
  check("serverInfo.version がデータの版と同じ",
        r.result.serverInfo.version === DB.version, r.result.serverInfo.version);
  check("使い方の但し書きに『算定の可否を判定しない』が入っている",
        r.result.instructions.includes("算定の可否を判定しない"));
}

console.log("\n2) 道具の一覧");
{
  const r = rpc("tools/list");
  const names = r.result.tools.map((t) => t.name);
  check("道具が11個ある", r.result.tools.length === 11, String(r.result.tools.length));
  check("すべてに説明と入力の型がある",
        r.result.tools.every((t) => t.name && t.description && t.inputSchema));
  check("弱いところを見る口がある",
        names.includes("jhnrd_unconfirmed") && names.includes("jhnrd_gaps") && names.includes("jhnrd_conflicts"));
  check("誰に養われているかを聞ける口がある", names.includes("jhnrd_disclosure"));
}

console.log("\n3) どの応答にも、断らない断りが付く");
{
  const minimal = { jhnrd_get_item: { id: DB.items[0].id }, jhnrd_search: { q: "訪問" },
                    jhnrd_get_source: { id: Object.keys(DB.sources)[0] } };
  let allEnvelope = true, allSay = true, allDisc = true;
  for (const t of TOOLS) {
    const out = call(t.name, minimal[t.name]);
    if (!out || out.version !== DB.version) { allEnvelope = false; console.log("     版が無い: " + t.name); }
    if (!out || !out.we_do_not_say) { allSay = false; console.log("     断りが無い: " + t.name); }
    if (!out || !out.disclosure) { allDisc = false; console.log("     開示が無い: " + t.name); }
  }
  check("11個すべてが版を名乗る", allEnvelope);
  check("11個すべてが『算定の可否は判定しない』を付ける", allSay);
  check("11個すべてが利益相反の開示を付ける", allDisc);
}

console.log("\n4) 断定を返さない");
{
  const minimal = { jhnrd_get_item: { id: DB.items[0].id }, jhnrd_search: { q: "加算" },
                    jhnrd_get_source: { id: Object.keys(DB.sources)[0] } };
  // 「算定できます」「該当します」を探す。ただし、
  //   (1) we_do_not_say の値(「…とは言わない」と書いてある欄。項目ごとにも持つ)
  //   (2) 鉤括弧で括られた言及(規律5の『「算定できます」とは言わない』など)
  // は、その語を「使っている」のではなく「取り上げている」ので除く。
  // 括弧の無い裸の断定だけを赤にする。
  const banned = ["算定できます", "該当します"];
  const mentions = ["『算定できます』", "「算定できます」", "『該当します』", "「該当します」"];
  let bad = [];
  for (const t of TOOLS) {
    const out = call(t.name, minimal[t.name]);
    let s = JSON.stringify(out, (k, v) => (k === "we_do_not_say" ? undefined : v));
    for (const m of mentions) s = s.split(m).join("");
    for (const b of banned) if (s.includes(b)) bad.push(t.name + ":" + b);
  }
  check("どの道具も『算定できます』『該当します』を返さない", bad.length === 0, bad.join(","));
}

console.log("\n5) 数が検査器と合う");
{
  const s = call("jhnrd_status");
  check("項目数が status.json と合う", s.items === STATUS.items, String(s.items));
  check("未確認の要件が status.json と合う",
        s.unconfirmed_requirements === STATUS.unconfirmed_requirements, String(s.unconfirmed_requirements));
  check("未解決の食い違いが status.json と合う", s.open_conflicts === STATUS.open_conflicts);
  check("現行の statute の数を別に出す", s.statute_current === STATUS.statute_current);
  check("網羅していないと自分から言う", /網羅した数字ではない/.test(s.not_a_complete_map));

  const li = call("jhnrd_list_items");
  check("一覧の件数が項目数と合う", li.count === DB.items.length, String(li.count));

  const un = call("jhnrd_unconfirmed");
  check("未確認の一覧が、検査器の数え方と同じ数を出す",
        un.counted_by_validator === STATUS.unconfirmed_requirements);
  check("未確認の一覧が空でない", un.count > 0, String(un.count));

  const ls = call("jhnrd_list_sources");
  check("出典の内訳が status.json と合う",
        ls.by_tier.statute === STATUS.sources.statute &&
        ls.by_tier.agency === STATUS.sources.agency &&
        ls.by_tier.secondary === STATUS.sources.secondary,
        JSON.stringify(ls.by_tier));
  check("現行の statute を分けて数えている",
        ls.current_by_tier.statute === STATUS.statute_current, String(ls.current_by_tier.statute));
}

console.log("\n6) 出典の素性が必ず付いてくる");
{
  const it = call("jhnrd_get_item", { id: "genzan-bcp" });
  check("項目が引ける", it.found === true);
  check("出典が解決されている", Array.isArray(it.sources_resolved) && it.sources_resolved.length > 0);
  check("どの出典にも tier が付く", it.sources_resolved.every((s) => s.missing || !!s.tier));
  check("どの出典にも現行かどうかが付く",
        it.sources_resolved.every((s) => s.missing || typeof s.current === "boolean"));
  check("tier が何を意味するかも一緒に返す",
        it.sources_resolved.every((s) => s.missing || !!s.tier_means));

  const src = call("jhnrd_get_source", { id: "mhlw-001195261" });
  check("出典1件が引ける", src.found === true);
  check("その出典を使っている項目を名指しできる", Array.isArray(src.used_by) && src.used_by.length > 0);
}

console.log("\n7) 無いものは、無いと言う");
{
  const miss = call("jhnrd_get_item", { id: "存在しない-id" });
  check("知らない id は found:false", miss.found === false);
  check("『制度に無い』と混同しないよう断る", /入っていないことは、制度に無いことを意味しない/.test(miss.note));
  check("引ける id を挙げる", Array.isArray(miss.available_ids) && miss.available_ids.length === DB.items.length);

  const none = call("jhnrd_search", { q: "ざぶとんの厚み" });
  check("見つからなければ 0 件", none.count === 0);
  check("見つからないことを『無い』と言わない", /制度に無いことを意味しない/.test(none.note));

  const hit = call("jhnrd_search", { q: "特別管理" });
  check("ある語なら見つかる", hit.count > 0, String(hit.count));
  check("どこで当たったかを言う", hit.hits.every((h) => Array.isArray(h.matched_in) && h.matched_in.length));

  const gaps = call("jhnrd_gaps");
  check("埋まっていないものを返す", Array.isArray(gaps.known_gaps));
  check("取りに行って取れなかった記録も返す", Array.isArray(gaps.attempts) && gaps.attempts.length > 0);
  check("解決済みは既定では出さない", gaps.known_gaps_count <= gaps.known_gaps_total);
  check("解決済みも頼めば出る",
        call("jhnrd_gaps", { include_resolved: true }).known_gaps_count === gaps.known_gaps_total);
}

console.log("\n8) 食い違いを、選ばずに返す");
{
  const c = call("jhnrd_conflicts");
  check("食い違いの記録が返る", c.count > 0, String(c.count));
  check("未解決の数を分けて出す", typeof c.open === "number");
  check("両方の言い分が残っている",
        c.conflicts.some((x) => x.claim_a && x.claim_b));
}

console.log("\n9) 誰に養われているかを言う");
{
  const d = call("jhnrd_disclosure");
  check("有償のサービスを売っていると書いてある", /有償のサービス/.test(d.conflict_of_interest));
  check("資金の出所を書いてある", /顧客からの対価のみ/.test(d.funding));
  check("顧客だけの別版は無いと書いてある", /別版・拡張版のデータは無い/.test(d.paid_customers_get_the_same_data));
  check("行政の確認は受けていないと書いてある", /行政の確認は受けていない/.test(d.not_endorsed));
  check("何で縛っているかも挙げる", d.what_is_bound_against_bias.length >= 5);

  const cite = call("jhnrd_how_to_cite");
  check("引用文に版が入る", cite.cite_as.includes(DB.version));
  check("なぜ版が要るかを言う", /版が違えば中身が違う/.test(cite.why_the_version_matters));
}

console.log("\n10) 口の作法");
{
  const bad = rpc("そんな method は無い");
  check("知らない method は -32601", bad.error && bad.error.code === -32601);
  check("通知(idなし)には応答を返さない", rpc("notifications/initialized", {}, null) === null);
  const t = rpc("tools/call", { name: "jhnrd_nonexistent", arguments: {} });
  check("知らない道具は isError で返す(例外にしない)", t.result && t.result.isError === true);
  check("使える道具を教える", t.result.content[0].text.includes("jhnrd_status"));
  check("resources/list は空で返す", rpc("resources/list").result.resources.length === 0);
  check("ping が返る", !!rpc("ping").result);
}

console.log("\n11) HTTP");
{
  const idx = await http("GET", "/");
  check("GET / が案内を返す", idx.status === 200 && idx.text.includes("JHNRD"));
  check("案内にも断りが入る", idx.text.includes("算定の可否は判定しない"));
  check("案内にも開示が入る", idx.text.includes("利益相反"));

  const st = await http("GET", "/status.json");
  check("GET /status.json が JSON を返す", st.status === 200 && st.json.items === STATUS.items);

  const one = await http("GET", "/items/" + encodeURIComponent("genzan-bcp"));
  check("GET /items/<id> が引ける", one.json.found === true);

  const q = await http("GET", "/search?q=" + encodeURIComponent("指示書"));
  check("GET /search?q= が引ける", q.json.count >= 0);

  const post = await http("POST", "/mcp", { jsonrpc: "2.0", id: 7, method: "tools/list" });
  check("POST /mcp が MCP として応える", post.json.id === 7 && post.json.result.tools.length === 11);

  const batch = await http("POST", "/mcp", [
    { jsonrpc: "2.0", id: 1, method: "ping" },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "ping" },
  ]);
  check("まとめて送られても、通知の分は返さない", batch.json.length === 2, String(batch.json.length));

  const opt = await http("OPTIONS", "/mcp");
  check("OPTIONS が 204", opt.status === 204);
  check("CORS が開いている", opt.res.headers.get("access-control-allow-origin") === "*");

  const put = await http("PUT", "/items");
  check("書き込みの口は無い(405)", put.status === 405);

  const getMcp = await http("GET", "/mcp");
  check("GET /mcp は 405(404ではない)", getMcp.status === 405, String(getMcp.status));
  check("405 のとき Allow を返す", getMcp.res.headers.get("allow") === "POST, OPTIONS");

  const nf = await http("GET", "/どこにもない");
  check("知らない道は 404", nf.status === 404);

  const broken = await http("POST", "/mcp", undefined);
  check("本文が無ければ 400", broken.status === 400);
}

console.log("");
// 確認や場面を足したら EXPECT も直すこと。数が合わないこと自体を赤にする。
const EXPECT = 72;
console.log("確かめた数: " + ran + " 件 (場面 11)");
if (ran !== EXPECT) {
  console.log("確かめた数が " + EXPECT + " と合わない。"
              + "途中で終わったか、確認を足して EXPECT を直していない。");
  process.exit(1);
}
if (fail) { console.log(fail + " 件おかしい。"); process.exit(1); }
console.log("公開MCP すべて通過 (" + ran + " 件)");
