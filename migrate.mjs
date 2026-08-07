#!/usr/bin/env node
// English Tracker 데이터 이전 스크립트 (구 공용 프로젝트 → 신규 전용 프로젝트).
//
// 사용법:
//   node migrate.mjs ./backup
//
// backup 폴더에 export_english_days.json / export_english_expressions.json 이 있어야 한다.
// 앱과 똑같이 익명 로그인으로 붙으므로 비밀번호는 필요 없다.

import { readFileSync } from "node:fs";
import { join } from "node:path";

const COLLECTIONS = ["english_days", "english_expressions"];

function readConfig() {
  const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
  const pick = (key) => html.match(new RegExp(`${key}:\\s*"([^"]+)"`))?.[1] ?? null;

  const apiKey = pick("apiKey");
  const projectId = pick("projectId");

  if (!apiKey || !projectId) {
    throw new Error("index.html 에서 apiKey/projectId 를 찾지 못했습니다.");
  }
  if (apiKey.startsWith("__") || projectId.startsWith("__")) {
    throw new Error("index.html 의 FIREBASE_CONFIG 가 아직 채워지지 않았습니다.");
  }
  if (projectId === "m-building-fbe46") {
    throw new Error("대상이 M Building 프로젝트입니다. 이전을 중단합니다.");
  }
  return { apiKey, projectId };
}

async function signInAnonymously(apiKey) {
  const res = await fetch(
    `https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ returnSecureToken: true }),
    },
  );
  const body = await res.json();
  if (!res.ok) {
    throw new Error(
      `익명 로그인 실패: ${body?.error?.message ?? res.status}\n` +
      "Authentication > Sign-in method 에서 '익명'이 사용 설정됐는지 확인하세요.",
    );
  }
  return body.idToken;
}

async function putDoc({ projectId, idToken }, collection, docId, fields) {
  const url =
    `https://firestore.googleapis.com/v1/projects/${projectId}` +
    `/databases/(default)/documents/${collection}/${encodeURIComponent(docId)}`;

  const res = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify({ fields }),
  });

  if (!res.ok) {
    throw new Error(`${collection}/${docId} 쓰기 실패 (${res.status}): ${await res.text()}`);
  }
}

async function main() {
  const backupDir = process.argv[2];
  if (!backupDir) {
    console.error("사용법: node migrate.mjs <backup 폴더 경로>");
    process.exit(1);
  }

  const { apiKey, projectId } = readConfig();
  console.log(`대상 프로젝트: ${projectId}`);

  const idToken = await signInAnonymously(apiKey);
  console.log("익명 로그인 성공.\n");

  let total = 0;
  for (const collection of COLLECTIONS) {
    const docs = JSON.parse(
      readFileSync(join(backupDir, `export_${collection}.json`), "utf8"),
    ).documents ?? [];

    for (const doc of docs) {
      await putDoc({ projectId, idToken }, collection, doc.name.split("/").pop(), doc.fields);
      total += 1;
    }
    console.log(`${collection}: ${docs.length}건 이전 완료`);
  }

  console.log(`\n총 ${total}건 이전 완료.`);
}

main().catch((err) => {
  console.error(`\n중단: ${err.message}`);
  process.exit(1);
});
