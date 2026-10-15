const SWAP_INTERVAL_MS = 10000;
const WINK_OUT_MS = 300;

const icon = document.querySelector('.identity-icon');
const ICONS = icon ? icon.dataset.icons.split(' ') : [];
let current = null;

function pickIcon() {
  let next;
  do {
    next = ICONS[Math.floor(Math.random() * ICONS.length)];
  } while (next === current && ICONS.length > 1);
  return next;
}

function showIcon(name) {
  if (current) icon.classList.remove(`fa-${current}`);
  current = name;
  icon.classList.add(`fa-${current}`);
  icon.classList.remove('wink-out');
  icon.classList.add('pop-in');
}

function swapIcon() {
  icon.classList.remove('pop-in');
  icon.classList.add('wink-out');
  setTimeout(() => showIcon(pickIcon()), WINK_OUT_MS);
}

if (icon) {
  showIcon(pickIcon());
  setInterval(swapIcon, SWAP_INTERVAL_MS);
}
