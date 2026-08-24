// JHNRD 公開MCP — 鍵なし・読み取り専用
//
// 何のためにあるか:
//   このデータベースの中身は CC BY 4.0 で公開されている。だが JSON を置いてあるだけでは、
//   道具として使うたびに誰かがパーサを書くことになる。書くたびに、書いた人の解釈が混ざる。
//   ここで配れば、混ざるのは一箇所で済む。
//
// 何をしないか:
//   算定の可否を判定しない。「該当します」「算定できます」を返さない。
//   どの応答にも we_do_not_say と、誰がこれを養っているか(disclosure)を必ず付ける。
//   書き込みの口は無い。鍵も要らない。誰の何も預からない。
//
// 版ずれについて:
//   配るデータは mcp/rules.data.js(生成物)。本体とずれたら CI が赤になる。
//   実行時に外へ取りに行かない。CDN の縁に古い版が残るのを、一度実際にやったため。

import { DB, STATUS } from "./rules.data.js";

const SERVER_NAME = "jhnrd";
const PROTOCOL_DEFAULT = "2025-06-18";
const PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"];
const REPO = "https://github.com/ogasurfproject-jpg/jhnrd";

const WE_DO_NOT_SAY =
  "算定の可否は判定しない。この口が言えるのは『この加算にはA・B・Cの要件があり、Cはまだ原文で確認できていない』までである。" +
  "『算定できます』『該当します』とは返さない。請求・届出の判断の前に、必ず原文を確認すること。";

const DISCLOSURE =
  "利益相反: この口を出している The HORIZONs株式会社は、このデータベースを裏付けにした有償のサービスを訪問看護事業所に売っている。" +
  "収入は顧客からの対価のみで、行政・業界団体・ベンダからの資金提供、掲載料、広告は受けていない。" +
  "有償の顧客だけが見られる別版のデータは無い。全文は " + REPO + "/blob/main/GOVERNANCE.md";

const TIERS = {
  statute: "告示・省令・通知の原文。最も強い。",
  agency: "厚生労働省が出した資料。原文ではない。",
  secondary: "民間の解説。単独では確定にしない。",
};

const INSTRUCTIONS =
  "訪問看護の算定要件データベース(JHNRD)。要件と、その要件がどの資料に基づくかを一つずつ持つ。\n" +
  "使うときの約束:\n" +
  "1. 数字を引いたら、必ず出典の tier(statute/agency/secondary)と current を一緒に示すこと。" +
  "『厚労省の資料』と『告示そのもの』を同じ扱いにしない。\n" +
  "2. confirmed:false の項目を、確認済みとして扱わない。unconfirmed_reason をそのまま伝えること。\n" +
  "3. 算定の可否を判定しない。この口も判定しない。\n" +
  "4. 版(version)を添えて引用すること。版が違えば中身が違う。\n" +
  "5. jhnrd_unconfirmed と jhnrd_gaps を先に見ると、このデータベースに何が無いかが分かる。" +
  "無いものを、無いと言えるようにするためにある。";

// ---------- 共通の封筒 ----------

function envelope(payload) {
  return Object.assign({
    version: DB.version,
    checked_at: STATUS.checked_at || null,
  }, payload, {
    we_do_not_say: WE_DO_NOT_SAY,
    disclosure: DISCLOSURE,
    license: "CC BY 4.0 — 版(version)を添えて引用すること",
    source_repository: REPO,
  });
}

function srcBrief(id) {
  const s = DB.sources[id];
  if (!s) return { id: id, missing: true };
  return {
    id: id,
    tier: s.tier,
    tier_means: TIERS[s.tier] || null,
    current: s.current === true,
    not_current_reason: s.not_current_reason || null,
    title: s.title,
    publisher: s.publisher || null,
    url: s.url || null,
    retrieved_at: s.retrieved_at || null,
  };
}

function refsOf(item) {
  const ids = [];
  const walk = (o) => {
    if (!o || typeof o !== "object") return;
    if (Array.isArray(o)) { o.forEach(walk); return; }
    for (const k of Object.keys(o)) {
      if (k === "source_ref" && Array.isArray(o[k])) {
        for (const r of o[k]) if (ids.indexOf(r) < 0) ids.push(r);
      } else walk(o[k]);
    }
  };
  walk(item);
  for (const r of (item.sources || [])) if (ids.indexOf(r) < 0) ids.push(r);
  return ids;
}

function itemBrief(it) {
  const eff = it.effect || {};
  return {
    id: it.id,
    kind: it.kind,
    insurance: it.insurance,
    name: it.name,
    effect_value: eff.value || null,
    effect_confirmed: eff.confirmed === true,
    unconfirmed_reason: eff.unconfirmed_reason || null,
    revision: eff.revision || it.revision || null,
    requirements: (it.requirements || []).length,
    requirements_unconfirmed: (it.requirements || []).filter(function (r) {
      return r.confirmed !== true;
    }).length,
    source_tiers: refsOf(it).map(function (id) {
      const s = DB.sources[id];
      return s ? (s.tier + (s.current === true ? "" : "(現行でない)")) : "?";
    }),
  };
}

// ---------- 道具 ----------

const TOOLS = [
  {
    name: "jhnrd_status",
    description: "このデータベースのいまの状態。版・項目数・出典の素性の内訳・未確認の要件の数・" +
      "未解決の食い違いの数。項目数は訪問看護の算定要件を網羅した数ではない。まずここを見ること。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "jhnrd_list_items",
    description: "収録している項目の一覧(要約)。insurance(介護/医療/介護・医療)と kind(加算/減算/単位数/" +
      "療養費/期限・交付ルール/振り分けルール)で絞れる。詳細は jhnrd_get_item。",
    inputSchema: {
      type: "object",
      properties: {
        insurance: { type: "string", description: "介護 / 医療 / 介護・医療 のいずれか(部分一致)" },
        kind: { type: "string", description: "加算 / 減算 / 単位数 / 療養費 / 期限・交付ルール / 振り分けルール" },
        only_unconfirmed: { type: "boolean", description: "true なら、確認できていないものだけ" },
      },
      additionalProperties: false,
    },
  },
  {
    name: "jhnrd_get_item",
    description: "項目1件の全部。要件・効果・期限に加えて、参照している出典を素性(tier)と現行かどうかつきで解決して返す。",
    inputSchema: {
      type: "object",
      properties: { id: { type: "string", description: "項目の id。例: genzan-bcp" } },
      required: ["id"], additionalProperties: false,
    },
  },
  {
    name: "jhnrd_search",
    description: "項目名・要件の本文・効果の文言を横断して探す。見つからなければ、見つからないと返す(推測しない)。",
    inputSchema: {
      type: "object",
      properties: {
        q: { type: "string", description: "探したい語。例: 特別管理加算 / ターミナル / 指示書" },
        limit: { type: "integer", description: "最大件数(既定 20)" },
      },
      required: ["q"], additionalProperties: false,
    },
  },
  {
    name: "jhnrd_unconfirmed",
    description: "原文で確認できていない要件の一覧と、なぜ確認できていないかの理由。" +
      "空欄にせず残してあるもの。このデータベースの弱いところを、先に見るための口。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "jhnrd_conflicts",
    description: "出典どうし、あるいは同じ出典の読み取りどうしが食い違った記録。解決済みも残す。" +
      "どちらかを選んで黙る、ということをしていない証拠でもある。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "jhnrd_gaps",
    description: "埋まっていないもの(known_gaps)、取りに行って取れなかった記録(attempts)、" +
      "途中まで分かったこと(findings)。何が無いかを、無いと言えるようにするための口。",
    inputSchema: {
      type: "object",
      properties: { include_resolved: { type: "boolean", description: "解決済みの gap も含める" } },
      additionalProperties: false,
    },
  },
  {
    name: "jhnrd_get_source",
    description: "出典1件の素性。tier(statute/agency/secondary)と、現行版かどうか(current)を必ず返す。",
    inputSchema: {
      type: "object",
      properties: { id: { type: "string", description: "出典の id。例: mhlw-001195261" } },
      required: ["id"], additionalProperties: false,
    },
  },
  {
    name: "jhnrd_list_sources",
    description: "出典の一覧。素性ごと、現行かどうかごとに数えたものも返す。" +
      "statute が何件あるかだけを言うと実態より良く見えるので、現行版の数を分けて出す。",
    inputSchema: {
      type: "object",
      properties: {
        tier: { type: "string", description: "statute / agency / secondary" },
        only_current: { type: "boolean", description: "true なら現行版の出典だけ" },
      },
      additionalProperties: false,
    },
  },
  {
    name: "jhnrd_disclosure",
    description: "誰がこれを作り、誰に養われているか。利益相反の開示。" +
      "出典の素性を名乗ることを規律にしている以上、この口自身の素性も名乗る。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "jhnrd_how_to_cite",
    description: "引用の仕方。版(seed 番号)を添えること。訂正しても元の記述を消さない方針のため、" +
      "版が分からないと後から突き合わせられない。",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
];

function norm(s) { return String(s == null ? "" : s).toLowerCase(); }

function callTool(name, args) {
  args = args || {};

  if (name === "jhnrd_status") {
    return envelope({
      dataset: DB.dataset,
      revision_note: DB.revision,
      items: STATUS.items,
      sources: STATUS.sources,
      sources_total: Object.keys(DB.sources).length,
      statute_current: STATUS.statute_current,
      sources_not_current: STATUS.sources_not_current,
      unconfirmed_requirements: STATUS.unconfirmed_requirements,
      conflicts_total: STATUS.conflicts_total,
      open_conflicts: STATUS.open_conflicts,
      field_reports: STATUS.field_reports,
      tiers: TIERS,
      discipline: DB.discipline,
      not_a_complete_map:
        STATUS.items + " 項目しかない。訪問看護の算定要件を網羅した数字ではない。" +
        "ここに無いことは『無い』ではなく『まだ入っていない』である。",
    });
  }

  if (name === "jhnrd_list_items") {
    let list = DB.items.slice();
    if (args.insurance) list = list.filter(function (x) { return norm(x.insurance).indexOf(norm(args.insurance)) >= 0; });
    if (args.kind) list = list.filter(function (x) { return norm(x.kind).indexOf(norm(args.kind)) >= 0; });
    if (args.only_unconfirmed === true) {
      list = list.filter(function (x) {
        return (x.effect && x.effect.confirmed !== true) ||
               (x.requirements || []).some(function (r) { return r.confirmed !== true; });
      });
    }
    return envelope({
      count: list.length,
      total_items: DB.items.length,
      filter: { insurance: args.insurance || null, kind: args.kind || null,
                only_unconfirmed: args.only_unconfirmed === true },
      items: list.map(itemBrief),
    });
  }

  if (name === "jhnrd_get_item") {
    const it = DB.items.filter(function (x) { return x.id === args.id; })[0];
    if (!it) {
      return envelope({
        found: false, asked_for: args.id,
        note: "その id の項目は入っていない。似た語で探すなら jhnrd_search。" +
              "入っていないことは、制度に無いことを意味しない。",
        available_ids: DB.items.map(function (x) { return x.id; }),
      });
    }
    return envelope({
      found: true,
      item: it,
      sources_resolved: refsOf(it).map(srcBrief),
      reading:
        "effect.confirmed が false のものは、原文で確認できていない。unconfirmed_reason をそのまま伝えること。" +
        "出典の tier が statute でも current が false なら、現行の根拠にはならない。",
    });
  }

  if (name === "jhnrd_search") {
    const q = norm(args.q);
    const limit = args.limit && args.limit > 0 ? args.limit : 20;
    if (!q) return envelope({ count: 0, hits: [], note: "探す語が空。" });
    const hits = [];
    for (const it of DB.items) {
      const where = [];
      if (norm(it.name).indexOf(q) >= 0) where.push("name");
      if (norm(it.id).indexOf(q) >= 0) where.push("id");
      if (norm(it.kind).indexOf(q) >= 0) where.push("kind");
      if (it.effect && norm(JSON.stringify(it.effect)).indexOf(q) >= 0) where.push("effect");
      const rq = (it.requirements || []).filter(function (r) { return norm(r.text).indexOf(q) >= 0; });
      if (rq.length) where.push("requirements");
      if (!where.length) continue;
      hits.push(Object.assign(itemBrief(it), {
        matched_in: where,
        matched_requirements: rq.map(function (r) {
          return { id: r.id, text: r.text, confirmed: r.confirmed === true,
                   unconfirmed_reason: r.unconfirmed_reason || null, ask: r.ask || null };
        }),
      }));
      if (hits.length >= limit) break;
    }
    return envelope({
      q: args.q, count: hits.length, hits: hits,
      note: hits.length ? null :
        "この語では見つからなかった。見つからないことは、制度に無いことを意味しない。" +
        "いま " + DB.items.length + " 項目しか入っていない。jhnrd_gaps に、埋まっていないものを書いてある。",
    });
  }

  if (name === "jhnrd_unconfirmed") {
    const out = [];
    for (const it of DB.items) {
      const eff = it.effect || {};
      if (eff.confirmed !== true && (eff.value || eff.unconfirmed_reason)) {
        out.push({ item_id: it.id, item_name: it.name, where: "effect",
                   text: eff.value || null, reason: eff.unconfirmed_reason || null });
      }
      for (const r of (it.requirements || [])) {
        if (r.confirmed !== true) {
          out.push({ item_id: it.id, item_name: it.name, where: "requirements",
                     requirement_id: r.id, text: r.text,
                     reason: r.unconfirmed_reason || null, ask: r.ask || null });
        }
      }
    }
    return envelope({
      count: out.length,
      counted_by_validator: STATUS.unconfirmed_requirements,
      unconfirmed: out,
      why_published:
        "空欄と未確認は違う。空欄にすると、確かめた上で無かったのか、確かめていないのかが区別できなくなる。",
    });
  }

  if (name === "jhnrd_conflicts") {
    const cs = (DB.conflicts || []).slice();
    for (const it of DB.items) {
      for (const c of (it.conflicts || [])) cs.push(Object.assign({ item_id: it.id }, c));
      for (const c of (it.read_conflicts || [])) cs.push(Object.assign({ item_id: it.id, read: true }, c));
    }
    return envelope({
      count: cs.length,
      open: cs.filter(function (c) { return !String(c.status || "").startsWith("解決"); }).length,
      note: DB.conflicts_note,
      conflicts: cs,
    });
  }

  if (name === "jhnrd_gaps") {
    let gaps = (DB.known_gaps || []);
    if (args.include_resolved !== true) gaps = gaps.filter(function (g) { return !g.resolved; });
    return envelope({
      known_gaps: gaps,
      known_gaps_count: gaps.length,
      known_gaps_total: (DB.known_gaps || []).length,
      attempts: DB.attempts || [],
      attempts_note: DB.attempts_note,
      findings: DB.findings || [],
      findings_note: DB.findings_note,
    });
  }

  if (name === "jhnrd_get_source") {
    const s = DB.sources[args.id];
    if (!s) {
      return envelope({ found: false, asked_for: args.id,
                        available_ids: Object.keys(DB.sources) });
    }
    return envelope({
      found: true,
      source: Object.assign({ id: args.id, tier_means: TIERS[s.tier] || null }, s),
      used_by: DB.items.filter(function (it) { return refsOf(it).indexOf(args.id) >= 0; })
                       .map(function (it) { return { id: it.id, name: it.name }; }),
    });
  }

  if (name === "jhnrd_list_sources") {
    let ids = Object.keys(DB.sources);
    if (args.tier) ids = ids.filter(function (i) { return DB.sources[i].tier === args.tier; });
    if (args.only_current === true) ids = ids.filter(function (i) { return DB.sources[i].current === true; });
    const by = { statute: 0, agency: 0, secondary: 0 };
    const cur = { statute: 0, agency: 0, secondary: 0 };
    for (const i of Object.keys(DB.sources)) {
      const s = DB.sources[i];
      if (by[s.tier] !== undefined) { by[s.tier]++; if (s.current === true) cur[s.tier]++; }
    }
    return envelope({
      count: ids.length,
      by_tier: by,
      current_by_tier: cur,
      tiers: TIERS,
      why_split:
        "素性(tier)が強いことと、いま有効であることは別。statute が何件あるかだけを言うと、実態より良く見える。",
      sources: ids.map(srcBrief),
    });
  }

  if (name === "jhnrd_disclosure") {
    return envelope({
      maintainer: "The HORIZONs株式会社 (法人番号 7021001075279)",
      author: "大賀俊勝 (ORCID 0009-0000-9180-903X)",
      conflict_of_interest:
        "このデータベースを裏付けにした有償のサービスを訪問看護事業所に販売している。" +
        "初期構築費と月額の形で対価を受け取っている。つまり、これが役に立つと思われることで、作っている側が収入を得る。",
      funding: "顧客からの対価のみ。行政・自治体・保険者・業界団体・ベンダ・製薬からの資金提供、助成、スポンサー、広告は無い。",
      listing_fees: "無い。載ること・載らないことに対して、誰からも対価を受け取っていない。",
      paid_customers_get_the_same_data:
        "有償の顧客だけが見られる別版・拡張版のデータは無い。公開されているものが全部。",
      not_endorsed:
        "一社が単独で維持している。査読機関でも公的機関でも業界団体でもない。" +
        "厚生労働省をはじめとする行政機関とは関係が無く、内容について行政の確認は受けていない。",
      what_is_bound_against_bias: [
        "項目数を先頭に置き、網羅した数字ではないと明記している",
        "未確認の要件の件数を公開している(空欄にしない)",
        "食い違いは両方残し、全件と未解決件数を分けて数える",
        "取りに行って取れなかった記録(attempts)も公開する",
        "訂正は元の記述を消さず、上に積む",
        "公開している数字は検査器の出力から機械生成しており、手で盛ると CI が落ちる",
      ],
      governance: REPO + "/blob/main/GOVERNANCE.md",
    });
  }

  if (name === "jhnrd_how_to_cite") {
    return envelope({
      cite_as:
        "The HORIZONs Inc. (2026). JHNRD — Japan Home-visit Nursing Reimbursement Database, " +
        "version " + DB.version + ". " + REPO + " (CC BY 4.0)",
      version: DB.version,
      tag: "seed." + (String(DB.version).split("seed.")[1] || "?"),
      why_the_version_matters:
        "版が違えば中身が違う。訂正しても元の記述を消さない方針のため、" +
        "どの版を見たかが分からないと、後から突き合わせられない。",
      machine_readable: {
        citation_cff: REPO + "/blob/main/CITATION.cff",
        datapackage: REPO + "/blob/main/datapackage.json",
        zenodo: REPO + "/blob/main/.zenodo.json",
        changelog: REPO + "/blob/main/CHANGELOG.md",
      },
      license: "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
    });
  }

  return null; // 知らない道具
}

// ---------- MCP (JSON-RPC over HTTP) ----------

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type, mcp-protocol-version, mcp-session-id, accept",
  "access-control-max-age": "86400",
};

function jsonResponse(obj, status) {
  return new Response(JSON.stringify(obj, null, 2), {
    status: status || 200,
    headers: Object.assign({ "content-type": "application/json; charset=utf-8" }, CORS),
  });
}

function rpcError(id, code, message, data) {
  const e = { code: code, message: message };
  if (data) e.data = data;
  return { jsonrpc: "2.0", id: id === undefined ? null : id, error: e };
}

export function handleRpc(msg) {
  // 返り値が null のときは、応答を返さない(通知)。
  if (!msg || msg.jsonrpc !== "2.0") {
    return rpcError(msg && msg.id, -32600, "JSON-RPC 2.0 ではない。");
  }
  const id = msg.id;
  const method = msg.method;

  if (id === undefined || id === null) {
    // 通知。initialized など。応答は返さない。
    return null;
  }

  if (method === "initialize") {
    const want = (msg.params && msg.params.protocolVersion) || PROTOCOL_DEFAULT;
    return {
      jsonrpc: "2.0", id: id,
      result: {
        protocolVersion: PROTOCOLS.indexOf(want) >= 0 ? want : PROTOCOL_DEFAULT,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: SERVER_NAME, title: "JHNRD 訪問看護 算定要件データベース", version: DB.version },
        instructions: INSTRUCTIONS,
      },
    };
  }

  if (method === "ping") return { jsonrpc: "2.0", id: id, result: {} };

  if (method === "tools/list") {
    return { jsonrpc: "2.0", id: id, result: { tools: TOOLS } };
  }

  if (method === "tools/call") {
    const p = msg.params || {};
    const out = callTool(p.name, p.arguments);
    if (out === null) {
      return {
        jsonrpc: "2.0", id: id,
        result: {
          isError: true,
          content: [{ type: "text", text: "そのような道具は無い: " + String(p.name) +
                      "\n使えるもの: " + TOOLS.map(function (t) { return t.name; }).join(", ") }],
        },
      };
    }
    return {
      jsonrpc: "2.0", id: id,
      result: { content: [{ type: "text", text: JSON.stringify(out, null, 2) }] },
    };
  }

  if (method === "resources/list") return { jsonrpc: "2.0", id: id, result: { resources: [] } };
  if (method === "prompts/list") return { jsonrpc: "2.0", id: id, result: { prompts: [] } };

  return rpcError(id, -32601, "知らない method: " + String(method));
}

const INDEX =
  "JHNRD — 訪問看護 算定要件データベース 公開MCP (鍵なし・読み取り専用)\n" +
  "版 " + DB.version + " / 項目 " + STATUS.items +
  " / 未確認の要件 " + STATUS.unconfirmed_requirements +
  " / 未解決の食い違い " + STATUS.open_conflicts + "\n\n" +
  "MCP:  POST /mcp   (JSON-RPC 2.0 / Streamable HTTP)  ※GET /mcp は 405\n" +
  "REST: GET /status.json  GET /items  GET /items/<id>  GET /sources  GET /sources/<id>\n" +
  "      GET /unconfirmed  GET /conflicts  GET /gaps  GET /disclosure  GET /cite\n\n" +
  WE_DO_NOT_SAY + "\n\n" + DISCLOSURE + "\n\n" + REPO + "\n";

const REST = {
  "/status.json": function () { return callTool("jhnrd_status", {}); },
  "/items": function (u) {
    return callTool("jhnrd_list_items", {
      insurance: u.searchParams.get("insurance") || undefined,
      kind: u.searchParams.get("kind") || undefined,
      only_unconfirmed: u.searchParams.get("only_unconfirmed") === "true" || undefined,
    });
  },
  "/sources": function (u) {
    return callTool("jhnrd_list_sources", {
      tier: u.searchParams.get("tier") || undefined,
      only_current: u.searchParams.get("only_current") === "true" || undefined,
    });
  },
  "/unconfirmed": function () { return callTool("jhnrd_unconfirmed", {}); },
  "/conflicts": function () { return callTool("jhnrd_conflicts", {}); },
  "/gaps": function (u) {
    return callTool("jhnrd_gaps", { include_resolved: u.searchParams.get("include_resolved") === "true" });
  },
  "/disclosure": function () { return callTool("jhnrd_disclosure", {}); },
  "/cite": function () { return callTool("jhnrd_how_to_cite", {}); },
  "/search": function (u) {
    return callTool("jhnrd_search", { q: u.searchParams.get("q") || "" });
  },
};

export async function handle(request) {
  const u = new URL(request.url);
  const path = u.pathname.replace(/\/+$/, "") || "/";

  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

  if (request.method === "POST" && (path === "/mcp" || path === "/")) {
    let body;
    try { body = await request.json(); }
    catch (e) { return jsonResponse(rpcError(null, -32700, "JSON として読めない。"), 400); }

    if (Array.isArray(body)) {
      const out = body.map(handleRpc).filter(function (x) { return x !== null; });
      return out.length ? jsonResponse(out) : new Response(null, { status: 202, headers: CORS });
    }
    const out = handleRpc(body);
    return out ? jsonResponse(out) : new Response(null, { status: 202, headers: CORS });
  }

  if (request.method === "GET" || request.method === "HEAD") {
    // Streamable HTTP では、GET /mcp は SSE の受け口である。
    // ここは SSE を出さない(server→client から先に話しかけることが無いため)。
    // 出さない実装は 404 ではなく 405 を返す、というのが作法。
    // 404 だと「この口自体が無い」と読めてしまう。
    if (path === "/mcp") {
      return new Response(
        JSON.stringify({
          error: "GET /mcp では受けない。MCP は POST /mcp。",
          note: "server→client から先に話しかけることが無いので、SSE の受け口は開けていない。",
          index: "/",
        }, null, 2),
        { status: 405, headers: Object.assign(
            { "content-type": "application/json; charset=utf-8", "allow": "POST, OPTIONS" }, CORS) });
    }
    if (path === "/") {
      return new Response(INDEX, {
        headers: Object.assign({ "content-type": "text/plain; charset=utf-8" }, CORS),
      });
    }
    if (REST[path]) return jsonResponse(REST[path](u));
    const mItem = path.match(/^\/items\/(.+)$/);
    if (mItem) return jsonResponse(callTool("jhnrd_get_item", { id: decodeURIComponent(mItem[1]) }));
    const mSrc = path.match(/^\/sources\/(.+)$/);
    if (mSrc) return jsonResponse(callTool("jhnrd_get_source", { id: decodeURIComponent(mSrc[1]) }));
    return jsonResponse({ error: "そのような道はない: " + path, index: "/" }, 404);
  }

  return jsonResponse({ error: "GET か POST のみ。書き込みの口は無い。" }, 405);
}

export { TOOLS, callTool, DISCLOSURE, WE_DO_NOT_SAY };
export default { fetch: handle };
