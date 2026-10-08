'use strict';

/* ================== СПРАВОЧНИКИ ================== */
const OPTIONS = {
  hair: {
    blonde: { label: 'Светлые',     color: '#e8c872' },
    light:  { label: 'Русые',       color: '#a9845a' },
    brown:  { label: 'Каштановые',  color: '#6b3f23' },
    black:  { label: 'Тёмные',      color: '#231a16' },
    red:    { label: 'Рыжие',       color: '#c4521f' },
    dyed:   { label: 'Цветные',     color: '#c86fd6' },
  },
  eyes: {
    blue:  { label: 'Голубые', color: '#4d93d9' },
    gray:  { label: 'Серые',   color: '#8a98a6' },
    green: { label: 'Зелёные', color: '#4f9a5a' },
    hazel: { label: 'Ореховые', color: '#9a7232' },
    brown: { label: 'Карие',   color: '#5a3518' },
  },
  body: {
    thin:   { label: 'Худощавое' },
    slim:   { label: 'Стройное' },
    sport:  { label: 'Спортивное' },
    medium: { label: 'Среднее' },
    big:    { label: 'Плотное' },
  },
  city: {
    msk: { label: 'Москва' }, spb: { label: 'Санкт-Петербург' }, kzn: { label: 'Казань' },
    nsk: { label: 'Новосибирск' }, ekb: { label: 'Екатеринбург' }, krd: { label: 'Краснодар' },
    min: { label: 'Минск' }, ala: { label: 'Алматы' },
  },
  goal: {
    love:    { label: 'Серьёзные отношения' },
    dates:   { label: 'Свидания' },
    friends: { label: 'Дружба' },
    chat:    { label: 'Общение' },
  },
  smoking: {
    no:  { label: 'Не курю' },
    rare:{ label: 'Иногда' },
    yes: { label: 'Курю' },
  },
  zodiac: Object.fromEntries(
    ['Овен','Телец','Близнецы','Рак','Лев','Дева','Весы','Скорпион','Стрелец','Козерог','Водолей','Рыбы']
      .map((z, i) => [`z${i}`, { label: z }])
  ),
};

const NAMES = {
  f: ['Анна','Мария','Алина','Дарья','Полина','Виктория','Ксения','Софья','Екатерина','Елизавета','Вероника','Арина',
      'Ульяна','Милана','Яна','Карина','Диана','Валерия','Кира','Алиса','Ева','Василиса','Злата','Таисия','Олеся','Юлия',
      'Камила','Амина','Ангелина','Марина','Настя','Лиля','Есения','Варвара'],
  m: ['Александр','Максим','Артём','Михаил','Даниил','Иван','Дмитрий','Кирилл','Егор','Никита','Матвей','Андрей',
      'Илья','Тимур','Роман','Арсений','Марк','Лев','Глеб','Владислав','Денис','Павел','Руслан','Сергей','Ярослав',
      'Богдан','Фёдор','Платон','Эмиль','Артур','Константин','Антон','Савелий','Гордей'],
};

const ABOUT = [
  'Люблю долгие прогулки и кофе навынос ☕', 'Ищу того, с кем не скучно молчать',
  'Работаю в IT, по выходным — горы 🏔', 'Обожаю собак, у меня их две 🐶🐶',
  'Готовлю лучшую пасту в городе, проверим?', 'Хожу в зал, читаю, иногда пишу музыку',
  'Путешествую при любой возможности ✈️', 'Студент(ка), учусь на дизайнера',
  'Не люблю переписки, давай сразу встретимся', 'Мемы — мой язык любви',
  'Кино по пятницам, спорт по утрам', 'Ищу компанию на концерты 🎸',
  'Немного интроверт, но с тобой разговорюсь', 'Катаюсь на сноуборде и велике',
  'Слушаю всё — от рэпа до джаза', 'Фотографирую закаты и котиков 📷',
];
const INTERESTS = ['спорт','музыка','кино','книги','игры','путешествия','танцы','кулинария','аниме','фото',
  'йога','бег','машины','искусство','театр','сериалы','походы','мода','животные','настолки'];

// Демо-фото: стоковые портреты моделей с Unsplash (https://unsplash.com/license).
// Параметры анкеты (волосы, глаза, рост) выдуманы и с фото не совпадают.
// Если фото не загрузилось, вместо него остаётся нарисованный аватар.
const PHOTOS = {
  f: ['photo-1494790108377-be9c29b29330', 'photo-1438761681033-6461ffad8d80', 'photo-1534528741775-53994a69daeb',
      'photo-1544005313-94ddf0286df2', 'photo-1517841905240-472988babdf9', 'photo-1524504388940-b1c1722653e1',
      'photo-1529626455594-4ff0802cfb7e', 'photo-1488426862026-3ee34a7d66df', 'photo-1531123897727-8f129e1688ce',
      'photo-1502823403499-6ccfcf4fb453', 'photo-1508214751196-bcfd4ca60f91', 'photo-1499952127939-9bbf5af6c51c'],
  m: ['photo-1500648767791-00dcc994a43e', 'photo-1507003211169-0a1dd7228f2d', 'photo-1506794778202-cad84cf45f1d',
      'photo-1539571696357-5a69c17a67c6', 'photo-1472099645785-5658abf4ff4e', 'photo-1519085360753-af0119f7cbe7',
      'photo-1492562080023-ab3db95bfbce', 'photo-1504257432389-52343af06ae3', 'photo-1522075469751-3a6694fb2f61',
      'photo-1463453091185-61582044d556', 'photo-1557862921-37829c790f19', 'photo-1488161628813-04466f872be2'],
};
const photoUrl = id => `https://images.unsplash.com/${id}?w=600&h=800&fit=crop&crop=faces&auto=format&q=70`;

const STORE_KEY = 'dating_state_v1';
const DEFAULT_FILTERS = {
  gender: 'f', ageMin: 18, ageMax: 35, heightMin: 140, heightMax: 210, weightMin: 40, weightMax: 130,
  hair: [], eyes: [], body: [], city: [], goal: [], smoking: [], zodiac: [],
};
const CHIP_GROUPS = ['hair', 'eyes', 'body', 'city', 'goal', 'smoking', 'zodiac'];
const MATCH_CHANCE = 0.4;

/* ================== ГЕНЕРАЦИЯ АНКЕТ ================== */
// Детерминированный ГСЧ, чтобы анкеты были одинаковыми при каждом заходе
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const rnd = mulberry32(20261008);
const pick = arr => arr[Math.floor(rnd() * arr.length)];
const between = (a, b) => a + Math.floor(rnd() * (b - a + 1));
const normal = (mean, sd) => {
  const u = 1 - rnd(), v = rnd();
  return mean + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
};
const weighted = obj => { // { key: weight }
  const total = Object.values(obj).reduce((s, w) => s + w, 0);
  let r = rnd() * total;
  for (const [k, w] of Object.entries(obj)) { if ((r -= w) < 0) return k; }
  return Object.keys(obj)[0];
};

const SKIN = ['#f6d7c3', '#f1c6a8', '#e5b08c', '#c98e66', '#a86d48', '#7a4a2e'];
const BG = [['#ff9a9e', '#fad0c4'], ['#a18cd1', '#fbc2eb'], ['#84fab0', '#8fd3f4'], ['#fccb90', '#d57eeb'],
  ['#e0c3fc', '#8ec5fc'], ['#f093fb', '#f5576c'], ['#4facfe', '#00f2fe'], ['#43e97b', '#38f9d7'], ['#fa709a', '#fee140']];

function bodyFromBmi(bmi) {
  if (bmi < 18.5) return 'thin';
  if (bmi < 21) return 'slim';
  if (bmi < 24) return rnd() < 0.5 ? 'sport' : 'medium';
  if (bmi < 26.5) return 'medium';
  return 'big';
}

function makeProfile(id, gender) {
  const f = gender === 'f';
  const age = Math.min(55, 18 + Math.floor(Math.abs(normal(0, 9))));
  const height = Math.round(Math.max(148, Math.min(205, normal(f ? 166 : 179, 7))));
  const bmi = Math.max(17, Math.min(31, normal(f ? 21 : 23.5, 2.5)));
  const weight = Math.round(bmi * (height / 100) ** 2);
  const interests = [...new Set(Array.from({ length: between(3, 5) }, () => pick(INTERESTS)))];
  return {
    id, gender, age, height, weight,
    name: pick(NAMES[gender]),
    hair: weighted(f ? { blonde: 4, light: 4, brown: 4, black: 4, red: 1.5, dyed: 1 }
                     : { blonde: 2, light: 5, brown: 5, black: 6, red: 1, dyed: 0.3 }),
    eyes: weighted({ blue: 3, gray: 3, green: 2, hazel: 2, brown: 5 }),
    body: bodyFromBmi(bmi),
    city: weighted({ msk: 5, spb: 4, kzn: 2, nsk: 2, ekb: 2, krd: 2, min: 2, ala: 1.5 }),
    goal: weighted({ love: 4, dates: 3, friends: 2, chat: 2 }),
    smoking: weighted({ no: 6, rare: 2, yes: 2 }),
    zodiac: `z${between(0, 11)}`,
    about: pick(ABOUT),
    interests,
    skin: pick(SKIN),
    bg: pick(BG),
    beard: !f && rnd() < 0.35,
    style: between(0, 2),
  };
}

const PROFILES = [];
for (let i = 0; i < 150; i++) PROFILES.push(makeProfile(`f${i}`, 'f'));
for (let i = 0; i < 150; i++) PROFILES.push(makeProfile(`m${i}`, 'm'));
// перемешиваем, чтобы лента не шла по порядку генерации
for (let i = PROFILES.length - 1; i > 0; i--) {
  const j = Math.floor(rnd() * (i + 1));
  [PROFILES[i], PROFILES[j]] = [PROFILES[j], PROFILES[i]];
}
const byId = Object.fromEntries(PROFILES.map(p => [p.id, p]));
// раздаём фото по кругу в порядке ленты
const photoIdx = { f: 0, m: 0 };
PROFILES.forEach(p => { const pool = PHOTOS[p.gender]; p.photo = pool[photoIdx[p.gender]++ % pool.length]; });

/* ================== АВАТАР (SVG) ================== */
let svgSeq = 0;
function avatar(p) {
  const uid = `g${++svgSeq}`;
  const hair = OPTIONS.hair[p.hair]?.color || '#333';
  const eye = OPTIONS.eyes[p.eyes]?.color || '#5a3518';
  const skin = p.skin || SKIN[1];
  const [c1, c2] = p.bg || BG[0];
  const f = p.gender === 'f';
  const backHair = f
    ? [`<path d="M48 112 Q46 38 100 38 Q154 38 152 112 L162 214 Q100 232 38 214 Z" fill="${hair}"/>`,
       `<path d="M52 110 Q50 40 100 40 Q150 40 148 110 L150 170 Q100 182 50 170 Z" fill="${hair}"/>`,
       `<circle cx="100" cy="36" r="24" fill="${hair}"/><path d="M54 108 Q52 46 100 44 Q148 46 146 108 Z" fill="${hair}"/>`][p.style || 0]
    : '';
  const frontHair = f
    ? `<path d="M56 104 Q58 50 100 50 Q142 50 144 104 Q128 70 104 68 Q84 72 56 104 Z" fill="${hair}"/>`
    : [`<path d="M57 98 Q54 46 100 45 Q146 46 143 98 Q138 70 100 68 Q62 70 57 98 Z" fill="${hair}"/>`,
       `<path d="M57 96 Q56 52 100 52 Q144 52 143 96 Q136 66 100 64 Q64 66 57 96 Z" fill="${hair}"/>`,
       `<path d="M58 92 Q60 40 104 42 Q150 46 142 98 Q132 62 96 64 Q70 64 58 92 Z" fill="${hair}"/>`][p.style || 0];
  const beard = p.beard
    ? `<path d="M62 118 Q64 162 100 166 Q136 162 138 118 Q132 146 100 148 Q68 146 62 118 Z" fill="${hair}" opacity=".9"/>` : '';
  const eyeEl = x => `<ellipse cx="${x}" cy="106" rx="8" ry="5.5" fill="#fff"/><circle cx="${x}" cy="106" r="4.4" fill="${eye}"/><circle cx="${x}" cy="106" r="1.9" fill="#111"/><circle cx="${x + 1.5}" cy="104.5" r="1" fill="#fff"/>`;
  return `<svg class="ava" viewBox="0 0 200 240" preserveAspectRatio="xMidYMin slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Аватар">
    <defs><linearGradient id="${uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs>
    <rect width="200" height="240" fill="url(#${uid})"/>
    ${backHair}
    <path d="M36 240 Q42 186 100 180 Q158 186 164 240 Z" fill="${f ? '#ffffff' : '#2b2d42'}" opacity=".92"/>
    <rect x="88" y="140" width="24" height="42" rx="8" fill="${skin}"/>
    <ellipse cx="100" cy="106" rx="42" ry="50" fill="${skin}"/>
    ${beard}
    ${frontHair}
    <path d="M78 94 Q85 90 92 94 M108 94 Q115 90 122 94" stroke="${hair}" stroke-width="3" fill="none" stroke-linecap="round"/>
    ${eyeEl(85)}${eyeEl(115)}
    <path d="M89 131 Q100 ${f ? 141 : 138} 111 131" stroke="${f ? '#c4505e' : '#7a3a2a'}" stroke-width="3" fill="none" stroke-linecap="round"/>
    ${f ? '<circle cx="74" cy="122" r="6" fill="#ff7b9c" opacity=".25"/><circle cx="126" cy="122" r="6" fill="#ff7b9c" opacity=".25"/>' : ''}
  </svg>`;
}

// Фото поверх нарисованного аватара; при ошибке загрузки фото убирается
function pic(p) {
  const img = p.photo
    ? `<img src="${photoUrl(p.photo)}" alt="" loading="lazy" draggable="false" onerror="this.remove()">` : '';
  return `<span class="pic">${avatar(p)}${img}</span>`;
}

/* ================== СОСТОЯНИЕ ================== */
function loadState() {
  try {
    const s = JSON.parse(localStorage.getItem(STORE_KEY));
    if (s && typeof s === 'object') {
      return { filters: { ...DEFAULT_FILTERS, ...s.filters }, seen: s.seen || [], likes: s.likes || [],
        matches: s.matches || [], messages: s.messages || {}, profile: s.profile || null };
    }
  } catch (e) { /* пусто или недоступно */ }
  return { filters: { ...DEFAULT_FILTERS }, seen: [], likes: [], matches: [], messages: {}, profile: null };
}
const state = loadState();
function save() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) { /* приватный режим */ }
}

/* ================== УТИЛИТЫ ================== */
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => [...root.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const label = (group, key) => OPTIONS[group]?.[key]?.label || '—';
function plural(n, one, few, many) {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
  return many;
}
const years = n => `${n} ${plural(n, 'год', 'года', 'лет')}`;

let toastTimer;
function toast(text) {
  const t = $('#toast');
  t.textContent = text;
  t.classList.add('is-show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('is-show'), 1800);
}

/* ================== ФИЛЬТРАЦИЯ ================== */
function matchesFilters(p, flt) {
  if (p.gender !== flt.gender) return false;
  if (p.age < flt.ageMin || p.age > flt.ageMax) return false;
  if (p.height < flt.heightMin || p.height > flt.heightMax) return false;
  if (p.weight < flt.weightMin || p.weight > flt.weightMax) return false;
  return CHIP_GROUPS.every(g => !flt[g].length || flt[g].includes(p[g]));
}
const candidates = (flt = state.filters) => PROFILES.filter(p => matchesFilters(p, flt));
const queue = () => candidates().filter(p => !state.seen.includes(p.id));

/* ================== КАРТОЧКА ================== */
function cardHtml(p, { full = false } = {}) {
  const tags = [
    p.height && `📏 ${p.height} см`, p.weight && `⚖️ ${p.weight} кг`,
    p.hair && `💇 ${label('hair', p.hair)}`, p.eyes && `👁 ${label('eyes', p.eyes)}`,
    p.body && `🏋️ ${label('body', p.body)}`, p.goal && `🎯 ${label('goal', p.goal)}`,
    p.smoking && `🚬 ${label('smoking', p.smoking)}`, p.zodiac && `✨ ${label('zodiac', p.zodiac)}`,
  ].filter(Boolean);
  return `
    <div class="card__photo">${pic(p)}
      <div class="card__title"><b>${esc(p.name)}${p.age ? `, ${p.age}` : ''}</b><span>📍 ${label('city', p.city)}</span></div>
    </div>
    <div class="card__body">
      <div class="tags">${tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
      ${p.about ? `<p class="about">${esc(p.about)}</p>` : ''}
      ${p.interests?.length ? `<div class="interests">${p.interests.map(i => `<span>#${esc(i)}</span>`).join('')}</div>` : ''}
      ${full && state.messages[p.id] ? `<p class="sent">💌 Ты написал(а): «${esc(state.messages[p.id])}»</p>` : ''}
    </div>`;
}

function renderFeed() {
  $$('#genderSwitch button').forEach(b => b.classList.toggle('is-active', b.dataset.gender === state.filters.gender));
  const total = candidates().length;
  const q = queue();
  $('#foundInfo').textContent = `Подходит: ${total} · осталось: ${q.length}`;
  const stage = $('#stage');
  const p = q[0];
  $('#actions').classList.toggle('is-disabled', !p);
  if (!p) {
    stage.innerHTML = `<div class="empty">
      <div class="empty__icon">🔍</div>
      <h3>${total ? 'Анкеты закончились' : 'Никого не нашлось'}</h3>
      <p>${total ? 'Ты посмотрел(а) всех, кто подходит под фильтры.' : 'Попробуй ослабить фильтры.'}</p>
      <div class="empty__btns">
        <button class="btn" data-go="filters">Изменить фильтры</button>
        ${total ? '<button class="btn btn--ghost" id="againBtn">Смотреть заново</button>' : ''}
      </div></div>`;
    $('#againBtn')?.addEventListener('click', () => {
      const ids = new Set(candidates().map(c => c.id));
      state.seen = state.seen.filter(id => !ids.has(id));
      save(); renderFeed();
    });
    return;
  }
  // следующая карточка подложкой — для эффекта стопки
  const next = q[1];
  stage.innerHTML = `${next ? `<article class="card card--under">${cardHtml(next)}</article>` : ''}
    <article class="card" id="topCard" data-id="${p.id}">${cardHtml(p)}
      <div class="stamp stamp--yes">ДА</div><div class="stamp stamp--no">НЕТ</div>
    </article>`;
  enableSwipe($('#topCard'));
  if (!hintShown) { hintShown = true; showSwipeHint($('#topCard')); }
}

// Анимация-подсказка: карточка качается вправо (ДА) и влево (НЕТ)
let hintShown = false;
function showSwipeHint(card) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  setTimeout(() => {
    if (!card.isConnected || busy) return;
    card.classList.add('card--hint');
    card.addEventListener('animationend', e => {
      if (e.target === card) card.classList.remove('card--hint');
    });
  }, 600);
}

/* ================== ДА / НЕТ ================== */
let busy = false;
function decide(liked, message = '') {
  const card = $('#topCard');
  if (!card || busy) return;
  busy = true;
  const id = card.dataset.id;
  card.style.transition = 'transform .35s ease, opacity .35s ease';
  card.style.transform = `translateX(${liked ? 140 : -140}%) rotate(${liked ? 22 : -22}deg)`;
  card.style.opacity = '0';

  state.seen.push(id);
  if (liked) {
    if (!state.likes.includes(id)) state.likes.push(id);
    if (message) state.messages[id] = message;
    // сообщение повышает шанс взаимности
    if (Math.random() < MATCH_CHANCE + (message ? 0.2 : 0)) {
      state.matches.push(id);
      setTimeout(() => showMatch(byId[id]), 380);
    }
  }
  save();
  renderBadges();
  setTimeout(() => { busy = false; renderFeed(); }, 340);
}

function enableSwipe(card) {
  let startX = 0, startY = 0, dx = 0, dragging = false;
  card.addEventListener('pointerdown', e => {
    if (busy) return;
    card.classList.remove('card--hint');
    dragging = true; startX = e.clientX; startY = e.clientY; dx = 0;
    card.setPointerCapture(e.pointerId);
    card.style.transition = 'none';
  });
  card.addEventListener('pointermove', e => {
    if (!dragging) return;
    dx = e.clientX - startX;
    const dy = (e.clientY - startY) * 0.3;
    card.style.transform = `translate(${dx}px, ${dy}px) rotate(${dx / 15}deg)`;
    card.style.setProperty('--yes', Math.max(0, Math.min(1, dx / 100)));
    card.style.setProperty('--no', Math.max(0, Math.min(1, -dx / 100)));
  });
  const end = () => {
    if (!dragging) return;
    dragging = false;
    if (Math.abs(dx) > 100) { decide(dx > 0); return; }
    card.style.transition = 'transform .25s ease';
    card.style.transform = '';
    card.style.setProperty('--yes', 0);
    card.style.setProperty('--no', 0);
  };
  card.addEventListener('pointerup', end);
  card.addEventListener('pointercancel', end);
}

/* ================== МОДАЛКИ ================== */
function openModal(html) {
  $('#modalBox').innerHTML = html;
  $('#modal').hidden = false;
}
function closeModal() { $('#modal').hidden = true; $('#modalBox').innerHTML = ''; }

function showMatch(p) {
  const her = p.gender === 'f';
  openModal(`<div class="match">
    <div class="match__title">💞 Взаимная симпатия!</div>
    <div class="match__ava">${pic(p)}</div>
    <p><b>${esc(p.name)}</b> тоже ${her ? 'лайкнула' : 'лайкнул'} тебя. ${her ? 'Напиши ей' : 'Напиши ему'} первым(ой)!</p>
    <div class="form-actions"><button class="btn btn--ghost" data-close>Смотреть дальше</button><button class="btn" data-go="matches" data-close>К парам</button></div>
  </div>`);
}

function askMessage() {
  const card = $('#topCard');
  if (!card) return;
  const p = byId[card.dataset.id];
  openModal(`<form class="msg" id="msgForm">
    <h3>💌 Сообщение для ${esc(p.name)}</h3>
    <textarea name="text" rows="4" maxlength="300" required placeholder="Привет! Увидел(а) твою анкету и..."></textarea>
    <div class="form-actions"><button type="button" class="btn btn--ghost" data-close>Отмена</button><button class="btn">Отправить ❤️</button></div>
  </form>`);
  const form = $('#msgForm');
  form.text.focus();
  form.addEventListener('submit', e => {
    e.preventDefault();
    const text = form.text.value.trim();
    if (!text) return;
    closeModal();
    toast('Сообщение отправлено');
    decide(true, text);
  });
}

function showProfile(id) {
  const p = byId[id];
  if (!p) return;
  const isMatch = state.matches.includes(id);
  openModal(`<article class="card card--static">${cardHtml(p, { full: true })}</article>
    <div class="form-actions">
      <button class="btn btn--ghost" data-remove="${id}">${isMatch ? 'Удалить пару' : 'Убрать лайк'}</button>
      <button class="btn" data-close>Закрыть</button>
    </div>`);
}

/* ================== ПАРЫ ================== */
function renderBadges() {
  $('#matchCount').textContent = state.matches.length;
  $('#matchCount').classList.toggle('is-zero', !state.matches.length);
}
function miniHtml(p) {
  return `<button class="mini" data-open="${p.id}">
    <span class="mini__ava">${pic(p)}</span>
    <span class="mini__info"><b>${esc(p.name)}, ${p.age}</b><small>${label('city', p.city)} · ${p.height} см · ${label('hair', p.hair).toLowerCase()}</small></span>
    ${state.messages[p.id] ? '<span class="mini__msg" title="Есть сообщение">💌</span>' : ''}
  </button>`;
}
function renderMatches() {
  const matches = state.matches.map(id => byId[id]).filter(Boolean).reverse();
  const likes = state.likes.filter(id => !state.matches.includes(id)).map(id => byId[id]).filter(Boolean).reverse();
  $('#matchList').innerHTML = matches.length ? matches.map(miniHtml).join('') : '<p class="muted">Пока пусто — лайкай анкеты 😉</p>';
  $('#likeList').innerHTML = likes.length ? likes.map(miniHtml).join('') : '<p class="muted">Ты ещё никого не лайкнул(а).</p>';
}

/* ================== ФИЛЬТРЫ (ФОРМА) ================== */
const filterForm = $('#filterForm');
let draft = structuredClone(state.filters);

function buildChips() {
  $$('.chips', filterForm).forEach(box => {
    const g = box.dataset.group;
    box.innerHTML = Object.entries(OPTIONS[g]).map(([k, o]) =>
      `<button type="button" class="chip" data-key="${k}">${o.color ? `<i style="background:${o.color}"></i>` : ''}${esc(o.label)}</button>`).join('');
    box.addEventListener('click', e => {
      const btn = e.target.closest('.chip');
      if (!btn) return;
      const k = btn.dataset.key;
      draft[g] = draft[g].includes(k) ? draft[g].filter(x => x !== k) : [...draft[g], k];
      syncFilterForm();
    });
  });
}

function syncFilterForm(force = true) {
  filterForm.gender.value = draft.gender;
  for (const k of ['ageMin', 'ageMax', 'heightMin', 'heightMax', 'weightMin', 'weightMax']) {
    // пока пользователь печатает число, не перетираем поле
    if (force || document.activeElement !== filterForm[k]) filterForm[k].value = draft[k];
  }
  $('#ageOut').textContent = `${draft.ageMin}–${draft.ageMax}`;
  $('#heightOut').textContent = `${draft.heightMin}–${draft.heightMax}`;
  $('#weightOut').textContent = `${draft.weightMin}–${draft.weightMax}`;
  CHIP_GROUPS.forEach(g => $$(`[data-group="${g}"] .chip`, filterForm)
    .forEach(c => c.classList.toggle('is-on', draft[g].includes(c.dataset.key))));
  $('#filterCount').textContent = candidates(draft).length;
}

function readNumber(name) {
  const v = parseInt(filterForm[name].value, 10);
  return Number.isFinite(v) ? v : DEFAULT_FILTERS[name];
}
filterForm.addEventListener('input', e => {
  if (e.target.name === 'gender') draft.gender = e.target.value;
  else if (e.target.type === 'number') draft[e.target.name] = readNumber(e.target.name);
  syncFilterForm(false);
});
// мин ≤ макс: если перепутали — меняем местами
function orderRanges() {
  for (const [a, b] of [['ageMin', 'ageMax'], ['heightMin', 'heightMax'], ['weightMin', 'weightMax']]) {
    if (draft[a] > draft[b]) [draft[a], draft[b]] = [draft[b], draft[a]];
  }
}
filterForm.addEventListener('change', () => { orderRanges(); syncFilterForm(); });
filterForm.addEventListener('submit', e => {
  e.preventDefault();
  orderRanges();
  state.filters = structuredClone(draft);
  save();
  showView('feed');
});
$('#filterReset').addEventListener('click', () => {
  draft = { ...structuredClone(DEFAULT_FILTERS), gender: draft.gender };
  syncFilterForm();
});

/* ================== МОЯ АНКЕТА ================== */
const profileForm = $('#profileForm');
function buildSelects() {
  $$('select[data-options]', profileForm).forEach(sel => {
    sel.innerHTML = Object.entries(OPTIONS[sel.dataset.options])
      .map(([k, o]) => `<option value="${k}">${esc(o.label)}</option>`).join('');
  });
}
function fillProfileForm() {
  const p = state.profile;
  if (!p) return;
  for (const k of ['name', 'age', 'height', 'weight', 'hair', 'eyes', 'city', 'about']) {
    if (p[k] != null) profileForm[k].value = p[k];
  }
  profileForm.gender.value = p.gender;
}
function renderProfilePreview() {
  const p = state.profile;
  $('#profilePreview').innerHTML = p
    ? `<h2>Так тебя видят другие</h2><article class="card card--static">${cardHtml({ ...p, skin: SKIN[1], bg: BG[4], style: 0 })}</article>`
    : '';
}
profileForm.addEventListener('submit', e => {
  e.preventDefault();
  const fd = new FormData(profileForm);
  const num = k => { const v = parseInt(fd.get(k), 10); return Number.isFinite(v) ? v : null; };
  const first = !state.profile;
  state.profile = {
    id: 'me', name: fd.get('name').trim(), gender: fd.get('gender'), age: num('age'),
    height: num('height'), weight: num('weight'), hair: fd.get('hair'), eyes: fd.get('eyes'),
    city: fd.get('city'), about: fd.get('about').trim(),
  };
  // при первом сохранении по умолчанию показываем противоположный пол
  if (first) { state.filters.gender = state.profile.gender === 'f' ? 'm' : 'f'; draft.gender = state.filters.gender; }
  save();
  renderProfilePreview();
  toast('Анкета сохранена');
});

/* ================== НАВИГАЦИЯ ================== */
function showView(name) {
  $$('.tab').forEach(t => t.classList.toggle('is-active', t.dataset.view === name));
  $$('.view').forEach(v => v.classList.toggle('is-active', v.id === `view-${name}`));
  if (name === 'feed') renderFeed();
  if (name === 'filters') { draft = structuredClone(state.filters); syncFilterForm(); }
  if (name === 'matches') renderMatches();
  if (name === 'profile') { fillProfileForm(); renderProfilePreview(); }
  window.scrollTo({ top: 0 });
}

$('#tabs').addEventListener('click', e => {
  const t = e.target.closest('.tab');
  if (t) showView(t.dataset.view);
});
$('#genderSwitch').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  state.filters.gender = b.dataset.gender;
  save(); renderFeed();
});
$('#btnYes').addEventListener('click', () => decide(true));
$('#btnNo').addEventListener('click', () => decide(false));
$('#btnMsg').addEventListener('click', askMessage);

document.addEventListener('keydown', e => {
  if (!$('#modal').hidden) { if (e.key === 'Escape') closeModal(); return; }
  if (!$('#view-feed').classList.contains('is-active') || e.target.matches('input, textarea, select')) return;
  if (e.key === 'ArrowRight') decide(true);
  if (e.key === 'ArrowLeft') decide(false);
});

document.addEventListener('click', e => {
  const go = e.target.closest('[data-go]');
  const open = e.target.closest('[data-open]');
  const remove = e.target.closest('[data-remove]');
  if (e.target.closest('[data-close]') || e.target.id === 'modal') closeModal();
  if (go) showView(go.dataset.go);
  if (open) showProfile(open.dataset.open);
  if (remove) {
    const id = remove.dataset.remove;
    state.likes = state.likes.filter(x => x !== id);
    state.matches = state.matches.filter(x => x !== id);
    delete state.messages[id];
    save(); closeModal(); renderBadges(); renderMatches();
  }
});

$('#resetSeen').addEventListener('click', () => {
  openModal(`<div class="msg"><h3>Сбросить просмотренные анкеты?</h3>
    <p class="muted">Лайки и пары останутся.</p>
    <div class="form-actions"><button class="btn btn--ghost" data-close>Отмена</button><button class="btn" id="confirmReset">Сбросить</button></div></div>`);
  $('#confirmReset').addEventListener('click', () => {
    state.seen = [];
    save(); closeModal(); toast('Можно смотреть заново'); showView('feed');
  });
});

/* ================== СТАРТ ================== */
buildChips();
buildSelects();
renderBadges();
renderFeed();
