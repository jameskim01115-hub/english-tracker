#!/usr/bin/env node
// 업무 회의 영어 문장을 Firestore 에 넣는다 (멱등: id = work-NNN). 사용: node upload-work.mjs work.json
import { readFileSync } from "node:fs";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const pick = k => html.match(new RegExp(`${k}:\\s*"([^"]+)"`))?.[1];
const apiKey = pick("apiKey"), projectId = pick("projectId");
if (!apiKey || !projectId || projectId === "m-building-fbe46") throw new Error("설정 확인 필요");
const REF = "https://jameskim01115-hub.github.io/english-tracker/";   // 키에 리퍼러 제한이 걸려 있다
const rows = JSON.parse(readFileSync(process.argv[2], "utf8"));
const auth = await (await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${apiKey}`,
  { method: "POST", headers: { "Content-Type": "application/json", Referer: REF }, body: JSON.stringify({ returnSecureToken: true }) })).json();
if (!auth.idToken) throw new Error("익명 로그인 실패");
const today = new Date(Date.now() + 8 * 3600e3).toISOString().slice(0, 10);   // 마닐라
const S = v => ({ stringValue: v }), N = v => ({ integerValue: String(v) });
let n = 0;
for (const [i, r] of rows.entries()) {
  const id = `work-${String(i + 1).padStart(3, "0")}`;
  const fields = {
    expression: S(r.en), meaning: S(r.ko), context: S(r.ctx), group: S(r.group),
    source: S("work"), slot: S(""), learnedDate: S(today), studied: { booleanValue: true }, studiedAt: S(today),
    stage: N(6), nextReview: S("9999-12-31"), seq: N(i + 1), origin: S(r.origin),
    createdAt: { timestampValue: new Date().toISOString() },
  };
  const url = `https://firestore.googleapis.com/v1/projects/${projectId}/databases/(default)/documents/english_expressions/${id}`;
  const res = await fetch(url, { method: "PATCH", headers: { "Content-Type": "application/json", Referer: REF, Authorization: `Bearer ${auth.idToken}` }, body: JSON.stringify({ fields }) });
  if (!res.ok) throw new Error(`${id} 실패 ${res.status}: ${await res.text()}`);
  n++;
}
console.log(`${n}건 업로드 (${projectId})`);
