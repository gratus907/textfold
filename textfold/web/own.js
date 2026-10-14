// This fork's changes to the pages, loaded right after i18n.js.
(() => {
  // English only: the interface speaks it, and texts are read in it (langs.py offers no translation).
  const i18n = window.DR_I18N;
  for (const code of Object.keys(i18n.NATIVE)) if (code !== 'en') delete i18n.NATIVE[code];
  i18n.CODES = ['en'];
  i18n.guess = () => 'en';
  document.head.append(Object.assign(document.createElement('style'), { textContent: '#ui-lang-box, .bar .sel, .bar .bar-sep { display: none; }' }));

  // A shared server (TEXTFOLD_HOST) keeps no reader's settings: this browser keeps its reader's own, API keys
  // included, sends them with each request to the server's API, and takes them back from a reply that changed them.
  const KEY = 'textfold-settings', plain = window.fetch;
  window.fetch = async (url, opt = {}) => {
    if (typeof url !== 'string' || !url.startsWith('/api/')) return plain(url, opt);
    let own = null;
    try { own = localStorage.getItem(KEY); } catch { /* private window */ }
    const r = await plain(url, own ? { ...opt, headers: { ...opt.headers, 'X-Textfold-Settings': own } } : opt);
    const changed = r.headers.get('X-Textfold-Settings');
    if (changed) try { localStorage.setItem(KEY, changed); } catch { /* private window */ }
    return r;
  };
})();
