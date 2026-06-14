"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const money = (n) =>
  "$" + (Number(n) || 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
const money2 = (n) =>
  "$" + (Number(n) || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    ...opts,
  });
  if (res.status === 401) {
    showLogin();
    throw new Error("unauthorized");
  }
  if (!res.ok) throw new Error("api " + res.status);
  return res.status === 204 ? null : res.json();
}

/* ---------------- Auth ---------------- */
function showLogin() {
  $("#app").classList.add("hidden");
  $("#login").classList.remove("hidden");
}
function showApp() {
  $("#login").classList.add("hidden");
  $("#app").classList.remove("hidden");
}

async function tryEnter() {
  try {
    await api("/api/summary");
    showApp();
    switchTab("home");
  } catch (_) {
    showLogin();
  }
}

$("#login-btn").addEventListener("click", doLogin);
$("#login-code").addEventListener("keydown", (e) => { if (e.key === "Enter") doLogin(); });

async function doLogin() {
  const code = $("#login-code").value.trim();
  const err = $("#login-error");
  err.textContent = "";
  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ code }),
    });
    if (!res.ok) { err.textContent = "Неверный код"; return; }
    showApp();
    switchTab("home");
  } catch (_) {
    err.textContent = "Ошибка соединения";
  }
}

/* ---------------- Toast ---------------- */
function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 1800);
}

/* ---------------- Tabs ---------------- */
const views = { home: viewHome, portfolio: viewPortfolio, bills: viewBills, advice: viewAdvice, add: viewAdd };
let current = "home";

function switchTab(tab) {
  current = tab;
  $$(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab && tab !== "add"));
  views[tab]();
}
$$(".tab").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));

/* ---------------- Views ---------------- */
function loading() {
  $("#view").innerHTML =
    '<div class="skeleton" style="height:150px"></div>' +
    '<div class="grid"><div class="skeleton" style="height:100px"></div>' +
    '<div class="skeleton" style="height:100px"></div></div>';
}

async function viewHome() {
  loading();
  const s = await api("/api/summary");
  const fr = Math.round(s.freedom_ratio * 100);
  const freeClass = s.today_free_cash > 0 ? "pos" : "neg";
  const v = $("#view");
  v.innerHTML = `
    <div class="page-head">
      <div><div class="greeting">Доброе утро,</div><div class="greeting"><b>${s.name}</b></div></div>
      <button class="icon-btn" id="sync"><svg viewBox="0 0 24 24"><path d="M4 4v6h6M20 20v-6h-6"/><path d="M20 9a8 8 0 0 0-14-3M4 15a8 8 0 0 0 14 3"/></svg></button>
    </div>

    <div class="hero">
      <div class="label">Net Worth</div>
      <div class="nw" id="nw">$0</div>
      <div class="sub">
        <span>Активы<b class="pos">${money(s.total_assets)}</b></span>
        <span>Долги<b class="neg">${money(s.total_liabilities)}</b></span>
        <span>Крипто<b>${money(s.total_crypto)}</b></span>
      </div>
    </div>

    <div class="card ring-card" style="margin-top:14px">
      <div class="ring" style="--p:${Math.min(fr,100)}"><b>${fr}%</b></div>
      <div class="ring-info">
        <h4>Путь к свободе 2030</h4>
        <p>Пассивный доход покрывает <b>${fr}%</b> расходов.${fr >= 100 ? " Цель достигнута!" : ` Осталось ${100 - fr}%.`}<br/>Запас прочности: ${s.survival_ratio.toFixed(1)} мес.</p>
      </div>
    </div>

    <div class="grid">
      <div class="card stat">
        <div class="k">Свободно сегодня</div>
        <div class="v ${freeClass}">${money(s.today_free_cash)}</div>
        <span class="chip ${s.today_free_cash > 0 ? "green" : "red"}">${s.today_free_cash > 0 ? "есть резерв" : "режим экономии"}</span>
      </div>
      <div class="card stat">
        <div class="k">Можно инвестировать</div>
        <div class="v">${money(s.investment_capacity)}</div>
        <span class="chip blue">после резервов</span>
      </div>
      <div class="card stat">
        <div class="k">Доступно (cash+банк)</div>
        <div class="v small">${money(s.available_cash)}</div>
      </div>
      <div class="card stat">
        <div class="k">Платежи 14 дней</div>
        <div class="v small">${money(s.upcoming_obligations_total)}</div>
        ${s.credit_utilization >= 0.5 ? '<span class="chip red">долг высокий</span>' : ""}
      </div>
    </div>

    <div class="card stat" style="margin-top:12px">
      <div class="k">Можно потратить на себя сегодня</div>
      <div class="v">${money2(s.personal_spending_allowance)}</div>
    </div>

    <p class="note"><span class="ro-badge">● read-only</span><br/>Система не переводит деньги и не торгует. AI предлагает — решаешь ты.</p>
  `;
  $("#sync").addEventListener("click", async (e) => {
    e.currentTarget.style.opacity = ".4";
    await api("/api/sync", { method: "POST" });
    toast("Синхронизировано");
    viewHome();
  });
  animateNumber($("#nw"), s.net_worth);
}

async function viewPortfolio() {
  loading();
  const p = await api("/api/portfolio");
  const v = $("#view");
  let rows = "";
  if (!p.holdings.length) {
    rows = '<div class="empty">Портфель пуст.<br/>Добавь активы во вкладке «+».</div>';
  } else {
    rows = p.holdings.map((h) => {
      const cls = h.action.includes("buy") ? "buy" : h.action.includes("reduce") ? "reduce" :
        h.action.includes("watch") ? "watch" : "hold";
      const label = h.action.includes("buy") ? "докупка" : h.action.includes("reduce") ? "снизить" :
        h.action.includes("watch") ? "следить" : "держать";
      return `
      <div class="row">
        <div class="l">
          <div class="coin">${h.symbol.slice(0, 4)}</div>
          <div><div class="name">${h.symbol}</div>
          <div class="meta">${h.amount} · ${h.location}</div>
          <div class="bar" style="width:120px"><i style="width:${Math.min(h.allocation_percent,100)}%"></i></div></div>
        </div>
        <div class="r"><div class="amt">${money(h.value)}</div>
        <div class="meta">${h.allocation_percent}%</div>
        <span class="pill ${cls}" style="margin-top:6px;display:inline-block">${label}</span></div>
      </div>`;
    }).join("");
  }
  v.innerHTML = `
    <div class="page-head"><h2>Портфель</h2></div>
    <div class="hero">
      <div class="label">Всего в крипте</div>
      <div class="nw">${money(p.total_value)}</div>
      <div class="sub"><span>На биржах<b class="${p.exchange_exposure_percent > 50 ? "neg" : "pos"}">${p.exchange_exposure_percent}%</b></span></div>
    </div>
    <div class="section-title">Активы</div>
    <div class="card" style="padding:4px 0">${rows}</div>
    ${p.exchange_exposure_percent > 50 ? '<p class="note">⚠️ Больше половины крипты на биржах. Рассмотри перевод на cold wallet.</p>' : ""}
  `;
}

async function viewBills() {
  loading();
  const [banks, obligations] = await Promise.all([api("/api/banks"), api("/api/obligations")]);
  const v = $("#view");
  const bankRows = banks.length ? banks.map((b) => `
    <div class="row">
      <div class="l"><div class="coin">${(b.name || "?").slice(0, 2).toUpperCase()}</div>
        <div><div class="name">${b.name}</div><div class="meta">${typeLabel(b.type)}${b.utilization != null ? " · " + b.utilization + "%" : ""}</div></div>
      </div>
      <div class="r"><div class="amt ${b.type === "credit_card" ? "neg" : ""}">${money2(b.balance)}</div>
      ${b.credit_limit ? `<div class="meta">лимит ${money(b.credit_limit)}</div>` : ""}</div>
    </div>`).join("") : '<div class="empty">Нет счетов. Добавь во вкладке «+».</div>';

  const oblRows = obligations.length ? obligations.map((o) => `
    <div class="row">
      <div class="l"><div class="coin" style="background:rgba(245,196,81,0.12)">${o.days_left}д</div>
        <div><div class="name">${o.name}</div><div class="meta">${o.due_date} · ${freqLabel(o.frequency)}</div></div>
      </div>
      <div class="r"><div class="amt">${money2(o.amount)}</div></div>
    </div>`).join("") : '<div class="empty">Нет ближайших платежей.</div>';

  v.innerHTML = `
    <div class="page-head"><h2>Платежи</h2></div>
    <div class="section-title">Банки и карты</div>
    <div class="card" style="padding:4px 0">${bankRows}</div>
    <div class="section-title">Ближайшие платежи</div>
    <div class="card" style="padding:4px 0">${oblRows}</div>
  `;
}

async function viewAdvice() {
  loading();
  const recs = await api("/api/recommendations");
  const v = $("#view");
  let body = recs.length ? recs.map((r) => {
    if (r.status !== "proposed")
      return `<div class="rec"><div class="top"><span class="sym">${r.symbol || "—"}</span>
        <span class="btn-done ${r.status === "approved" ? "chip green" : "chip red"}">${r.status === "approved" ? "одобрено" : "отклонено"}</span></div>
        <div class="reason">${r.reason || ""}</div></div>`;
    return `<div class="rec" data-id="${r.id}">
      <div class="top"><span class="sym">${r.symbol || "—"} · ${money2(r.amount_suggested)}</span>
        <span class="pill watch">риск ${r.risk_level || "?"}</span></div>
      <div class="reason">${r.reason || ""}</div>
      <div class="acts">
        <button class="btn-sm btn-ok" data-act="approve">Одобрить</button>
        <button class="btn-sm btn-no" data-act="reject">Отклонить</button>
      </div></div>`;
  }).join("") : '<div class="empty">Сегодня свободных денег для инвестиций нет.<br/>Главное — сохранить cashflow.</div>';

  v.innerHTML = `
    <div class="page-head"><h2>Совет дня</h2></div>
    <div class="card" style="padding:4px 0">${body}</div>
    <details class="accordion" style="margin-top:16px">
      <summary>Полный отчёт <span class="muted">▾</span></summary>
      <div class="body"><div class="report-box" id="report">Загрузка…</div></div>
    </details>
    <p class="note">Любая рекомендация требует твоего подтверждения. Никаких автопокупок.</p>
  `;
  $$(".rec .btn-sm").forEach((btn) => btn.addEventListener("click", async (e) => {
    const card = e.target.closest(".rec");
    const id = card.dataset.id;
    const act = e.target.dataset.act;
    await api(`/api/recommendations/${id}/${act}`, { method: "POST" });
    toast(act === "approve" ? "Одобрено" : "Отклонено");
    viewAdvice();
  }));
  const det = $(".accordion");
  det.addEventListener("toggle", async () => {
    if (det.open && $("#report").textContent === "Загрузка…") {
      const r = await api("/api/report");
      $("#report").textContent = r.text;
    }
  }, { once: false });
}

function viewAdd() {
  const v = $("#view");
  v.innerHTML = `
    <div class="page-head"><h2>Добавить</h2></div>

    <details class="accordion" open>
      <summary>Наличные <span class="muted">▾</span></summary>
      <div class="body">
        <div class="seg" id="cash-seg">
          <button class="on" data-t="cash_income">Доход</button>
          <button data-t="cash_expense">Расход</button>
        </div>
        <div class="field"><label>Сумма ($)</label><input id="cash-amt" type="number" inputmode="decimal" placeholder="300"/></div>
        <div class="field"><label>Описание</label><input id="cash-desc" placeholder="работа / еда"/></div>
        <button class="btn-primary" id="cash-save">Сохранить</button>
      </div>
    </details>

    <details class="accordion">
      <summary>Карта / счёт <span class="muted">▾</span></summary>
      <div class="body">
        <div class="field"><label>Название</label><input id="card-name" placeholder="Credit One"/></div>
        <div class="field"><label>Тип</label><select id="card-type">
          <option value="credit_card">Кредитная карта</option>
          <option value="checking">Расчётный счёт</option>
          <option value="savings">Накопительный</option>
          <option value="loan">Кредит</option>
        </select></div>
        <div class="field"><label>Баланс ($)</label><input id="card-bal" type="number" inputmode="decimal" placeholder="120"/></div>
        <div class="field"><label>Кредитный лимит ($, для карт)</label><input id="card-lim" type="number" inputmode="decimal" placeholder="300"/></div>
        <button class="btn-primary" id="card-save">Сохранить</button>
      </div>
    </details>

    <details class="accordion">
      <summary>Платёж / обязательство <span class="muted">▾</span></summary>
      <div class="body">
        <div class="field"><label>Название</label><input id="ob-name" placeholder="Аренда машины"/></div>
        <div class="field"><label>Сумма ($)</label><input id="ob-amt" type="number" inputmode="decimal" placeholder="399"/></div>
        <div class="field"><label>Дата платежа</label><input id="ob-date" type="date"/></div>
        <div class="field"><label>Периодичность</label><select id="ob-freq">
          <option value="one_time">Разовый</option><option value="monthly">Ежемесячно</option>
          <option value="weekly">Еженедельно</option><option value="yearly">Ежегодно</option>
        </select></div>
        <button class="btn-primary" id="ob-save">Сохранить</button>
      </div>
    </details>

    <details class="accordion">
      <summary>Профиль (расходы / пассивный доход) <span class="muted">▾</span></summary>
      <div class="body" id="profile-body"><p class="muted">Загрузка…</p></div>
    </details>
  `;

  let cashType = "cash_income";
  $$("#cash-seg button").forEach((b) => b.addEventListener("click", () => {
    $$("#cash-seg button").forEach((x) => x.classList.remove("on"));
    b.classList.add("on"); cashType = b.dataset.t;
  }));
  $("#cash-save").addEventListener("click", async () => {
    const amount = parseFloat($("#cash-amt").value);
    if (!amount) return toast("Введи сумму");
    await api("/api/cash", { method: "POST", body: JSON.stringify({ amount, type: cashType, description: $("#cash-desc").value }) });
    toast("Записано"); $("#cash-amt").value = ""; $("#cash-desc").value = "";
  });
  $("#card-save").addEventListener("click", async () => {
    const name = $("#card-name").value.trim();
    if (!name) return toast("Введи название");
    await api("/api/card", { method: "POST", body: JSON.stringify({
      name, account_type: $("#card-type").value,
      current_balance: parseFloat($("#card-bal").value) || 0,
      credit_limit: parseFloat($("#card-lim").value) || null,
    }) });
    toast("Карта добавлена"); $("#card-name").value = ""; $("#card-bal").value = ""; $("#card-lim").value = "";
  });
  $("#ob-save").addEventListener("click", async () => {
    const name = $("#ob-name").value.trim();
    const due = $("#ob-date").value;
    if (!name || !due) return toast("Заполни название и дату");
    await api("/api/obligations", { method: "POST", body: JSON.stringify({
      name, amount: parseFloat($("#ob-amt").value) || 0, due_date: due, frequency: $("#ob-freq").value,
    }) });
    toast("Платёж добавлен"); $("#ob-name").value = ""; $("#ob-amt").value = "";
  });

  $(".accordion:last-child").addEventListener("toggle", async function () {
    if (!this.open) return;
    const s = await api("/api/settings");
    $("#profile-body").innerHTML = `
      <div class="field"><label>Имя</label><input id="p-name" value="${s.name || ""}"/></div>
      <div class="field"><label>Расходы в месяц ($)</label><input id="p-exp" type="number" value="${s.monthly_expenses || 0}"/></div>
      <div class="field"><label>Пассивный доход в месяц ($)</label><input id="p-pas" type="number" value="${s.passive_income || 0}"/></div>
      <div class="field"><label>Подушка безопасности ($)</label><input id="p-buf" type="number" value="${s.emergency_buffer || 0}"/></div>
      <button class="btn-primary" id="p-save">Сохранить профиль</button>`;
    $("#p-save").addEventListener("click", async () => {
      await api("/api/settings", { method: "POST", body: JSON.stringify({
        name: $("#p-name").value,
        monthly_expenses: parseFloat($("#p-exp").value) || 0,
        passive_income: parseFloat($("#p-pas").value) || 0,
        emergency_buffer: parseFloat($("#p-buf").value) || 0,
      }) });
      toast("Профиль обновлён");
    });
  });
}

/* ---------------- helpers ---------------- */
function typeLabel(t) {
  return { credit_card: "кредитка", checking: "счёт", savings: "накопит.", loan: "кредит",
    investment: "инвест", cash: "наличные" }[t] || t;
}
function freqLabel(f) {
  return { one_time: "разовый", monthly: "ежемесячно", weekly: "еженедельно",
    biweekly: "раз в 2 нед.", yearly: "ежегодно" }[f] || f;
}
function animateNumber(el, target) {
  const dur = 700, start = performance.now();
  function frame(now) {
    const t = Math.min((now - start) / dur, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = money(target * eased);
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

/* ---------------- boot ---------------- */
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
tryEnter();
