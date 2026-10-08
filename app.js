// Фотографии — с Unsplash (бесплатная лицензия, https://unsplash.com/license)
const img = (id) => `https://images.unsplash.com/${id}?w=800&q=80&auto=format&fit=crop`;

const PRODUCTS = [
  { id: 1, name: 'Футболка Basic', category: 'Футболки', price: 2490, image: img('photo-1521572163474-6864f9cf17ab'), sizes: ['XS', 'S', 'M', 'L', 'XL'], badge: 'Хит',
    desc: 'Плотная футболка из 100% хлопка, 240 г/м². Свободный крой, не теряет форму после стирки.' },
  { id: 2, name: 'Футболка Oversize Black', category: 'Футболки', price: 2790, image: img('photo-1503341504253-dff4815485f1'), sizes: ['S', 'M', 'L', 'XL'],
    desc: 'Оверсайз-футболка со спущенным плечом. Глубокий чёрный цвет, который не выгорает.' },
  { id: 3, name: 'Футболка Graphic', category: 'Футболки', price: 3190, oldPrice: 3990, image: img('photo-1583743814966-8936f5b7be1a'), sizes: ['S', 'M', 'L'],
    desc: 'Футболка с принтом шелкографией. Лимитированный тираж.' },
  { id: 4, name: 'Худи Heavy Grey', category: 'Худи', price: 5990, image: img('photo-1556821840-3a63f95609a7'), sizes: ['S', 'M', 'L', 'XL'], badge: 'Новинка',
    desc: 'Тяжёлое худи из футера с начёсом, 450 г/м². Двойной капюшон, карман-кенгуру.' },
  { id: 5, name: 'Худи Essential', category: 'Худи', price: 5490, image: img('photo-1620799140408-edc6dcb6d633'), sizes: ['XS', 'S', 'M', 'L', 'XL'],
    desc: 'Базовое худи на каждый день. Мягкий хлопок, рибана на манжетах и поясе.' },
  { id: 6, name: 'Свитшот Crew', category: 'Худи', price: 4490, oldPrice: 5290, image: img('photo-1578587018452-892bacefd3f2'), sizes: ['S', 'M', 'L', 'XL'],
    desc: 'Свитшот с круглым вырезом. Свободная посадка, плотный трикотаж.' },
  { id: 7, name: 'Куртка Leather', category: 'Куртки', price: 14990, image: img('photo-1551028719-00167b16eac5'), sizes: ['S', 'M', 'L'],
    desc: 'Байкерская куртка из мягкой экокожи. Металлическая фурнитура, подкладка из вискозы.' },
  { id: 8, name: 'Джинсовая куртка', category: 'Куртки', price: 7990, image: img('photo-1576995853123-5a10305d93c0'), sizes: ['S', 'M', 'L', 'XL'], badge: 'Хит',
    desc: 'Классическая джинсовая куртка свободного кроя из плотного денима.' },
  { id: 9, name: 'Бомбер Olive', category: 'Куртки', price: 9490, image: img('photo-1591047139829-d91aecb6caea'), sizes: ['M', 'L', 'XL'],
    desc: 'Лёгкий бомбер с утеплителем. Подойдёт на межсезонье.' },
  { id: 10, name: 'Джинсы Straight', category: 'Низ', price: 6490, image: img('photo-1542272604-787c3835535d'), sizes: ['28', '30', '32', '34', '36'],
    desc: 'Прямые джинсы с высокой посадкой. 100% хлопок, без стрейча.' },
  { id: 11, name: 'Карго Wide', category: 'Низ', price: 5790, image: img('photo-1624378439575-d8705ad7ae80'), sizes: ['S', 'M', 'L', 'XL'], badge: 'Новинка',
    desc: 'Широкие брюки-карго с объёмными карманами. Плотный твил.' },
  { id: 12, name: 'Кепка Logo', category: 'Аксессуары', price: 1990, image: img('photo-1588850561407-ed78c282e89b'), sizes: ['One size'],
    desc: 'Шестипанельная кепка с вышитым логотипом. Регулируемая застёжка.' },
];

const PROMOS = { SK1M10: 0.10, WELCOME: 0.15 };
const FREE_SHIPPING_FROM = 5000;
const SHIPPING = { courier: 390, pickup: 290 };

// --- Состояние ---
const store = {
  get(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* приватный режим */ }
  },
};

let cart = store.get('sk1m_cart', []); // [{ id, size, qty }]
let promo = store.get('sk1m_promo', null);
let filter = 'Все';
let sort = 'default';

const $ = (s, root = document) => root.querySelector(s);
const fmt = (n) => n.toLocaleString('ru-RU') + ' ₽';
const byId = (id) => PRODUCTS.find((p) => p.id === id);

// Подставляем заглушку, если фото не загрузилось
document.addEventListener('error', (e) => {
  const el = e.target;
  if (el.tagName !== 'IMG' || el.dataset.failed) return;
  el.dataset.failed = '1';
  const ph = document.createElement('div');
  ph.className = 'img-fallback';
  ph.textContent = el.dataset.fallback || el.alt || 'SK1MSUKA';
  if (el.classList.contains('about__img')) ph.style.cssText = 'aspect-ratio:4/5;border-radius:14px';
  el.replaceWith(ph);
}, true);

// --- Каталог ---
function renderFilters() {
  const cats = ['Все', ...new Set(PRODUCTS.map((p) => p.category))];
  $('#filters').innerHTML = cats
    .map((c) => `<button class="chip ${c === filter ? 'active' : ''}" data-cat="${c}">${c}</button>`)
    .join('');
}

function priceHtml(p) {
  return `<span class="price">${p.oldPrice ? `<s>${fmt(p.oldPrice)}</s>` : ''}${fmt(p.price)}</span>`;
}

function renderGrid() {
  let list = PRODUCTS.filter((p) => filter === 'Все' || p.category === filter);
  if (sort === 'price-asc') list = [...list].sort((a, b) => a.price - b.price);
  if (sort === 'price-desc') list = [...list].sort((a, b) => b.price - a.price);
  if (sort === 'name') list = [...list].sort((a, b) => a.name.localeCompare(b.name, 'ru'));

  $('#grid').innerHTML = list.map((p) => `
    <article class="card" data-id="${p.id}">
      <div class="card__media">
        <img src="${p.image}" alt="${p.name}" loading="lazy">
        ${p.oldPrice ? '<span class="badge badge--sale">Скидка</span>' : p.badge ? `<span class="badge">${p.badge}</span>` : ''}
        <button class="card__quick" data-quick="${p.id}">Быстрый просмотр</button>
      </div>
      <div class="card__info">
        <div><div class="card__name">${p.name}</div><div class="card__cat">${p.category}</div></div>
        ${priceHtml(p)}
      </div>
    </article>`).join('');
}

$('#filters').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-cat]');
  if (!btn) return;
  filter = btn.dataset.cat;
  renderFilters();
  renderGrid();
});
$('#sort').addEventListener('change', (e) => { sort = e.target.value; renderGrid(); });
$('#grid').addEventListener('click', (e) => {
  const card = e.target.closest('.card');
  if (card) openProduct(Number(card.dataset.id));
});

// --- Модалки и корзина ---
const overlay = $('#overlay');
let openLayer = null;

function openLayerEl(el) {
  closeLayer();
  openLayer = el;
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  overlay.classList.add('open');
  document.body.classList.add('locked');
}
function closeLayer() {
  if (!openLayer) return;
  openLayer.classList.remove('open');
  openLayer.setAttribute('aria-hidden', 'true');
  openLayer = null;
  overlay.classList.remove('open');
  document.body.classList.remove('locked');
}
overlay.addEventListener('click', closeLayer);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLayer(); });
document.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', closeLayer));

function openProduct(id) {
  const p = byId(id);
  let size = p.sizes.length === 1 ? p.sizes[0] : null;
  let qty = 1;

  const body = $('#productBody');
  body.innerHTML = `
    <div class="product">
      <div class="product__media"><img src="${p.image}" alt="${p.name}"></div>
      <div class="product__info">
        <div class="card__cat">${p.category}</div>
        <h3>${p.name}</h3>
        ${priceHtml(p)}
        <p class="product__desc">${p.desc}</p>
        <div>
          <div class="label">Размер</div>
          <div class="sizes">${p.sizes.map((s) => `<button class="size ${s === size ? 'active' : ''}" data-size="${s}">${s}</button>`).join('')}</div>
        </div>
        <div class="product__actions">
          <div class="qty"><button data-q="-1" aria-label="Меньше">−</button><span id="pQty">1</span><button data-q="1" aria-label="Больше">+</button></div>
          <button class="btn btn--dark" id="addBtn">В корзину</button>
        </div>
        <p class="muted">Бесплатная доставка от ${fmt(FREE_SHIPPING_FROM)} · Возврат 14 дней</p>
      </div>
    </div>`;

  body.onclick = (e) => {
    const s = e.target.closest('[data-size]');
    if (s) {
      size = s.dataset.size;
      body.querySelectorAll('.size').forEach((b) => b.classList.toggle('active', b === s));
    }
    const q = e.target.closest('[data-q]');
    if (q) {
      qty = Math.max(1, Math.min(10, qty + Number(q.dataset.q)));
      $('#pQty').textContent = qty;
    }
    if (e.target.id === 'addBtn') {
      if (!size) {
        body.querySelectorAll('.size').forEach((b) => {
          b.classList.remove('error'); void b.offsetWidth; b.classList.add('error');
        });
        toast('Выбери размер');
        return;
      }
      addToCart(p.id, size, qty);
      closeLayer();
      toast(`«${p.name}» (${size}) добавлен в корзину`);
    }
  };

  openLayerEl($('#productModal'));
}

function addToCart(id, size, qty = 1) {
  const item = cart.find((i) => i.id === id && i.size === size);
  if (item) item.qty = Math.min(10, item.qty + qty);
  else cart.push({ id, size, qty });
  saveCart();
  const c = $('#cartCount');
  c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump');
}

function saveCart() {
  cart = cart.filter((i) => i.qty > 0 && byId(i.id));
  store.set('sk1m_cart', cart);
  store.set('sk1m_promo', promo);
  renderCart();
}

function calcTotals(delivery = 'courier') {
  const subtotal = cart.reduce((sum, i) => sum + byId(i.id).price * i.qty, 0);
  const discount = promo ? Math.round(subtotal * PROMOS[promo]) : 0;
  const shipping = subtotal === 0 || subtotal - discount >= FREE_SHIPPING_FROM ? 0 : SHIPPING[delivery];
  return { subtotal, discount, shipping, total: subtotal - discount + shipping };
}

function totalsHtml(t) {
  return `
    <div><span>Товары</span><span>${fmt(t.subtotal)}</span></div>
    ${t.discount ? `<div class="discount"><span>Скидка (${promo})</span><span>−${fmt(t.discount)}</span></div>` : ''}
    <div><span>Доставка</span><span>${t.shipping ? fmt(t.shipping) : 'Бесплатно'}</span></div>
    <div class="total"><span>Итого</span><span>${fmt(t.total)}</span></div>`;
}

function renderCart() {
  const count = cart.reduce((n, i) => n + i.qty, 0);
  $('#cartCount').textContent = count;

  if (!cart.length) {
    $('#cartItems').innerHTML = `
      <div class="empty">
        <p>В корзине пока пусто</p>
        <button class="btn btn--dark" id="toShop">Перейти в магазин</button>
      </div>`;
    $('#cartFoot').hidden = true;
    return;
  }
  $('#cartFoot').hidden = false;

  $('#cartItems').innerHTML = cart.map((i, idx) => {
    const p = byId(i.id);
    return `
      <div class="cart-item">
        <div class="cart-item__img"><img src="${p.image}" alt="${p.name}"></div>
        <div>
          <div class="cart-item__name">${p.name}</div>
          <div class="cart-item__meta">Размер: ${i.size} · ${fmt(p.price)}</div>
          <div class="qty"><button data-dec="${idx}" aria-label="Меньше">−</button><span>${i.qty}</span><button data-inc="${idx}" aria-label="Больше">+</button></div>
        </div>
        <div class="cart-item__right">
          <span class="price">${fmt(p.price * i.qty)}</span>
          <button class="remove" data-remove="${idx}">Удалить</button>
        </div>
      </div>`;
  }).join('');

  const t = calcTotals();
  const left = FREE_SHIPPING_FROM - (t.subtotal - t.discount);
  $('#totals').innerHTML = totalsHtml(t) +
    (left > 0 ? `<p class="muted">Добавь ещё на ${fmt(left)} — и доставка будет бесплатной</p>` : '');
  $('#promoInput').value = promo || '';
}

$('#cartItems').addEventListener('click', (e) => {
  const d = e.target.dataset;
  if (d.inc !== undefined) cart[d.inc].qty = Math.min(10, cart[d.inc].qty + 1);
  else if (d.dec !== undefined) cart[d.dec].qty -= 1;
  else if (d.remove !== undefined) cart.splice(Number(d.remove), 1);
  else if (e.target.id === 'toShop') { closeLayer(); location.hash = 'shop'; return; }
  else return;
  saveCart();
});

$('#promoForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const code = $('#promoInput').value.trim().toUpperCase();
  if (!code) { promo = null; saveCart(); return; }
  if (PROMOS[code]) {
    promo = code;
    saveCart();
    toast(`Промокод применён: −${PROMOS[code] * 100}%`);
  } else {
    toast('Такого промокода нет');
  }
});

$('#cartOpen').addEventListener('click', () => { renderCart(); openLayerEl($('#cart')); });

// --- Оформление заказа ---
const checkoutBodyHtml = $('#checkoutBody').innerHTML;

function updateCheckoutTotals() {
  $('#checkoutTotals').innerHTML = totalsHtml(calcTotals($('#checkoutForm').delivery.value));
}

$('#checkoutBtn').addEventListener('click', () => {
  if (!cart.length) return;
  openLayerEl($('#checkoutModal'));
  updateCheckoutTotals();
});

function bindCheckout(form) {
  form.delivery.addEventListener('change', updateCheckoutTotals);
  form.addEventListener('input', (e) => e.target.classList.remove('invalid'));
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let ok = true;
    form.querySelectorAll('input').forEach((input) => {
      const valid = input.checkValidity();
      input.classList.toggle('invalid', !valid);
      if (!valid) ok = false;
    });
    if (!ok) { toast('Проверь выделенные поля'); return; }

    const order = Math.floor(100000 + Math.random() * 900000);
    const t = calcTotals(form.delivery.value);
    const name = form.name.value.trim().split(' ')[0];
    const email = form.email.value.trim();
    cart = [];
    promo = null;
    saveCart();

    const body = $('#checkoutBody');
    body.innerHTML = `
      <div class="success">
        <div class="success__icon">✓</div>
        <h3>Спасибо, ${escapeHtml(name)}!</h3>
        <p>Заказ №${order} на сумму ${fmt(t.total)} оформлен.<br>Подтверждение придёт на ${escapeHtml(email)}.</p>
        <button class="btn btn--dark" id="successClose">Продолжить покупки</button>
      </div>`;
    $('#successClose').addEventListener('click', () => {
      closeLayer();
      setTimeout(resetCheckout, 300);
    });
  });
}

function resetCheckout() {
  const body = $('#checkoutBody');
  if (body.querySelector('#checkoutForm')) return;
  body.innerHTML = checkoutBodyHtml;
  bindCheckout($('#checkoutForm'));
}

// После закрытия окна успеха возвращаем форму на место
overlay.addEventListener('click', () => setTimeout(resetCheckout, 300));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setTimeout(resetCheckout, 300); });
document.querySelectorAll('#checkoutModal [data-close]').forEach((b) => b.addEventListener('click', () => setTimeout(resetCheckout, 300)));

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// --- Прочее ---
let toastTimer;
function toast(text) {
  const t = $('#toast');
  t.textContent = text;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2400);
}

$('#newsletter').addEventListener('submit', (e) => {
  e.preventDefault();
  e.target.reset();
  toast('Готово! Промокод SK1M10 на скидку 10% уже твой');
});

const nav = $('#nav');
$('#burger').addEventListener('click', () => nav.classList.toggle('open'));
nav.addEventListener('click', (e) => { if (e.target.tagName === 'A') nav.classList.remove('open'); });

renderFilters();
renderGrid();
renderCart();
bindCheckout($('#checkoutForm'));
