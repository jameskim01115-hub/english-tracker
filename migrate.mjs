#!/usr/bin/env node
// English Tracker 데이터 이전 스크립트 (m-building-fbe46 → 신규 전용 프로젝트).
//
// 사용법:
//   node migrate.mjs ./backup
//
// backup 폴더에는 export_english_days.json / export_english_expressions.json 이 있어야 한다.
// 비밀번호는 이 스크립트가 직접 입력받아 Firebase에만 보내며, 화면에도 파일에도 남지 않는다.

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createInterface } from "node:readline";

const COLLECTIONS = ["english_days", "english_expressions"];

// ── index.html 에서 신규 프로젝트 설정을 읽는다 ──────────────────────────
function readConfig() {
  const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
  const pick = (key) => {
    const m = html.match(new RegExp(`${key}:\\s*"([^"]+)"`));
    return m ? m[1] : null;
  };
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

// ── 입력 ────────────────────────────────────────────────────────────────
function ask(question, { hidden = false } = {}) {
  return new Promise((resolve) => {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    if (!hidden) {
      rl.question(question, (answer) => { rl.close(); resolve(answer.trim()); });
      return;
    }
    // 비밀번호는 화면에 찍지 않는다.
    process.stdout.write(question);
    const onData = (char) => {
      if (["\n", "\r", ""].includes(char.toString())) {
        process.stdin.removeListener("data", onData);
        return;
      }
      process.stdout.write("*");
    };
    process.stdin.on("data", onData);
    rl.question("", (answer) => {
      process.stdin.removeListener("data", onData);
      rl.close();
      process.stdout.write("\n");
      resolve(answer);
    });
  });
}

// ── Firebase ────────────────────────────────────────────────────────────
async function signIn(apiKey, email, password) {
  const res = await fetch(
    `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, returnSecureToken: true }),
    },
  );
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`로그인 실패: ${body?.error?.message ?? res.status}`);
  }
  return { idToken: body.idToken, uid: body.localId };
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
    const body = await res.text();
    throw new Error(`${collection}/${docId} 쓰기 실패 (${res.status}): ${body}`);
  }
}

// ── 실행 ────────────────────────────────────────────────────────────────
async function main() {
  const backupDir = process.argv[2];
  if (!backupDir) {
    console.error("사용법: node migrate.mjs <backup 폴더 경로>");
    process.exit(1);
  }

  const { apiKey, projectId } = readConfig();
  console.log(`대상 프로젝트: ${projectId}\n`);

  const email = await ask("이메일: ");
  const password = await ask("비밀번호: ", { hidden: true });

  const { idToken, uid } = await signIn(apiKey, email, password);
  console.log(`\n로그인 성공. UID: ${uid}`);
  console.log("이 UID를 firestore.rules 의 __PATRICK_UID__ 자리에 넣으세요.\n");

  let total = 0;
  for (const collection of COLLECTIONS) {
    const path = join(backupDir, `export_${collection}.json`);
    const docs = JSON.parse(readFileSync(path, "utf8")).documents ?? [];

    for (const doc of docs) {
      const docId = doc.name.split("/").pop();
      await putDoc({ projectId, idToken }, collection, docId, doc.fields);
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
