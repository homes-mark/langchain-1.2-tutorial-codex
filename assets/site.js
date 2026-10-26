/* Offline only: no fetch, CDN, telemetry or service worker. */
(() => {
  'use strict';
  const key = 'langchain12-cn-progress-v1';
  const links = [...document.querySelectorAll('.course-nav a[data-page]')];
  const slugs = links.map(a => a.dataset.page);
  const current = document.body.dataset.slug;
  const box = document.querySelector('#page-complete');
  const message = document.querySelector('#progress-message');
  let persistent = true;
  let done = new Set();
  const valid = value => Array.isArray(value) && value.every(x => typeof x === 'string' && slugs.includes(x));
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    if (valid(saved)) done = new Set(saved);
    localStorage.setItem(key, JSON.stringify([...done]));
  } catch (_) { persistent = false; }
  // Carry state in local HTML links as a fallback for file:// storage policies.
  const incoming = new URLSearchParams(location.search).get('done');
  if (incoming !== null) {
    const list = incoming ? incoming.split(',') : [];
    if (valid(list)) done = new Set(list);
  }
  function render() {
    box.checked = done.has(current);
    document.querySelector('#progress-text').textContent = `${done.size} / ${slugs.length}`;
    document.querySelector('#course-progress').value = done.size;
    links.forEach(a => {
      a.classList.toggle('done', done.has(a.dataset.page));
      a.title = done.has(a.dataset.page) ? '已完成' : '待学习';
    });
    const state = slugs.filter(s => done.has(s)).join(',');
    document.querySelectorAll('a[href]').forEach(a => {
      const raw = a.getAttribute('href');
      if (!/^[\w-]+\.html(?:[?#]|$)/.test(raw)) return;
      const url = new URL(raw, location.href);
      url.searchParams.set('done', state);
      a.setAttribute('href', url.pathname.split('/').pop() + url.search + url.hash);
    });
    try { localStorage.setItem(key, JSON.stringify([...done])); } catch (_) { persistent = false; }
    try {
      const url = new URL(location.href);
      url.searchParams.set('done', state);
      history.replaceState(null, '', url);
    } catch (_) { /* Export remains available in restrictive local browsers. */ }
    document.querySelector('#progress-note').textContent = persistent
      ? '本地保存；通过站内链接携带进度。可导出备份。'
      : '浏览器限制本地存储；站内跳转可保留进度，退出前请导出。';
  }
  box.addEventListener('change', () => { box.checked ? done.add(current) : done.delete(current); render(); });
  document.querySelector('#export-progress').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({schema: key, completed: [...done]}, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'langchain12-progress.json'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    message.textContent = '已导出学习进度。';
  });
  document.querySelector('#import-progress').addEventListener('change', async event => {
    try {
      const file = event.target.files[0];
      if (!file) return;
      if (file.size > 100000) throw new Error('文件过大');
      const data = JSON.parse(await file.text());
      if (data.schema !== key || !valid(data.completed)) throw new Error('不是本教程的有效进度文件');
      done = new Set(data.completed); render(); message.textContent = '进度已恢复。';
    } catch (error) { message.textContent = `导入失败：${error.message}`; }
    event.target.value = '';
  });
  document.querySelector('#nav-search').addEventListener('input', event => {
    const query = event.target.value.trim().toLowerCase();
    links.forEach(a => { a.hidden = !a.textContent.toLowerCase().includes(query); });
  });
  document.querySelector('#menu-toggle').addEventListener('click', event => {
    const open = document.querySelector('#sidebar').classList.toggle('open');
    event.currentTarget.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.copy-code').forEach(button => button.addEventListener('click', async () => {
    const code = button.closest('.codebox').querySelector('code').textContent;
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(code);
      else {
        const text = document.createElement('textarea'); text.value = code;
        text.style.position = 'fixed'; text.style.opacity = '0'; document.body.append(text); text.select();
        const success = document.execCommand('copy'); text.remove();
        if (!success) throw new Error('clipboard unavailable');
      }
      button.textContent = '已复制';
    } catch (_) { button.textContent = '请选中代码复制'; }
    setTimeout(() => { button.textContent = '复制代码'; }, 1800);
  }));
  render();
})();
