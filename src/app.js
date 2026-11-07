
(function(){
  document.body.classList.add('js-enabled');
  const pages=[...document.querySelectorAll('.page-section')];
  const nav=[...document.querySelectorAll('.nav-item')];
  const defaultId=pages.length?pages[0].id:'';
  function pageForHash(hash){
    const id=(hash||'').replace(/^#/,'');
    if(!id) return document.getElementById(defaultId);
    const direct=document.getElementById(id);
    if(direct && direct.classList.contains('page-section')) return direct;
    if(direct) return direct.closest('.page-section');
    return document.getElementById(defaultId);
  }
  function showFromHash(){
    const target=pageForHash(location.hash);
    if(!target) return;
    pages.forEach(p=>p.classList.toggle('active',p===target));
    nav.forEach(a=>a.classList.toggle('active',a.dataset.navPage===target.id));
    const raw=(location.hash||'').replace(/^#/,'');
    const exact=raw?document.getElementById(raw):null;
    setTimeout(()=> {
      if(exact && exact!==target) exact.scrollIntoView({block:'start'});
      else window.scrollTo({top:0,behavior:'auto'});
    },0);
    document.title=(target.dataset.title||'Информатика')+' — единый HTML';
  }
  window.addEventListener('hashchange',showFromHash);
  showFromHash();
  const search=document.getElementById('page-search');
  if(search){
    search.addEventListener('input',function(){
      const q=this.value.trim().toLowerCase();
      nav.forEach(a=>a.style.display=(!q || (a.dataset.search||'').includes(q))?'block':'none');
    });
  }
})();

(function () {
  const toggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('menu-backdrop');
  const mobile = window.matchMedia('(max-width: 900px)');
  const storageKey = 'informatika.sidebar.collapsed';
  let desktopCollapsed = false;
  try { desktopCollapsed = localStorage.getItem(storageKey) === 'true'; } catch (_) {}
  function setCollapsed(collapsed, restoreFocus = false) {
    if (collapsed && (restoreFocus || sidebar.contains(document.activeElement))) toggle.focus();
    document.body.classList.toggle('menu-collapsed', collapsed);
    toggle.setAttribute('aria-expanded', String(!collapsed));
    toggle.setAttribute('aria-label', collapsed ? 'Показать меню' : 'Скрыть меню');
    sidebar.inert = collapsed;
    backdrop.hidden = collapsed || !mobile.matches;
  }
  toggle.addEventListener('click', () => {
    const collapsed = !document.body.classList.contains('menu-collapsed');
    setCollapsed(collapsed);
    if (!mobile.matches) {
      desktopCollapsed = collapsed;
      try { localStorage.setItem(storageKey, String(collapsed)); } catch (_) {}
    }
  });
  backdrop.addEventListener('click', () => setCollapsed(true, true));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !document.body.classList.contains('menu-collapsed')) {
      setCollapsed(true, true);
    }
  });
  sidebar.addEventListener('click', event => {
    if (mobile.matches && event.target.closest('a[href^="#"]')) setCollapsed(true, true);
  });
  mobile.addEventListener('change', () => setCollapsed(mobile.matches || desktopCollapsed));
  setCollapsed(mobile.matches || desktopCollapsed);
})();
