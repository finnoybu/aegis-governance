/**
 * AEGIS Ecosystem Navigation Bar
 * Shared component loaded by all AEGIS sites to provide cross-domain navigation.
 *
 * Usage: <script src="https://aegis-initiative.com/shared/aegis-nav.js" defer></script>
 *
 * The bar auto-detects the current domain and highlights the active site.
 * It reads [data-theme] from <html> to match each site's light/dark mode.
 * It pushes page content down by setting a CSS variable on <html>.
 */
(function () {
  'use strict';

  // ── Configuration ──────────────────────────────────────────────────
  // The hub link (diamond + "AEGIS Initiative") always links to Initiative.
  // Only peer sites go in SITES — Initiative is NOT listed here.
  var SITES = [
    { id: 'constitution', label: 'Constitution', domain: 'aegis-constitution.com', url: 'https://aegis-constitution.com', visible: true },
    { id: 'governance',   label: 'Governance',   domain: 'aegis-governance.com',   url: 'https://aegis-governance.com',   visible: true },
    { id: 'docs',         label: 'Docs',         domain: 'aegis-docs.com',         url: 'https://aegis-docs.com',         visible: true },
    { id: 'federation',   label: 'Federation',   domain: 'aegis-federation.com',   url: 'https://aegis-federation.com',   visible: true },
    { id: 'labs',         label: 'Labs',         domain: 'aegis-labs.dev',         url: 'https://aegis-labs.dev',         visible: false },
    { id: 'sdk',          label: 'SDK',          domain: 'aegis-sdk.dev',          url: 'https://aegis-sdk.dev',          visible: false },
    { id: 'platform',     label: 'Platform',     domain: 'aegis-platform.net',     url: 'https://aegis-platform.net',     visible: false },
  ];

  var HUB_URL = 'https://aegis-initiative.com';
  var HUB_DOMAIN = 'aegis-initiative.com';
  var NAV_HEIGHT = 32;

  // ── Detect current site ────────────────────────────────────────────
  var hostname = window.location.hostname;
  var activeSite = null;

  // Check if we're on the hub site itself
  if (hostname === HUB_DOMAIN || hostname === 'www.' + HUB_DOMAIN) {
    activeSite = 'initiative';
  } else {
    for (var i = 0; i < SITES.length; i++) {
      if (hostname === SITES[i].domain || hostname === 'www.' + SITES[i].domain) {
        activeSite = SITES[i].id;
        break;
      }
    }
  }

  // ── Push page content down ─────────────────────────────────────────
  document.documentElement.style.setProperty('--aegis-nav-height', NAV_HEIGHT + 'px');

  // ── Build the nav bar inside a Shadow DOM ──────────────────────────
  var host = document.createElement('div');
  host.id = 'aegis-ecosystem-nav';
  host.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;height:' + NAV_HEIGHT + 'px;';
  var shadow = host.attachShadow({ mode: 'open' });

  // ── Styles ─────────────────────────────────────────────────────────
  var style = document.createElement('style');
  style.textContent = [
    /* Reset & host */
    ':host { display: block; }',
    '*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }',

    /* Bar */
    '.aegis-nav {',
    '  display: flex;',
    '  align-items: center;',
    '  height: ' + NAV_HEIGHT + 'px;',
    '  padding: 0 1rem;',
    '  font-family: "IBM Plex Sans", system-ui, -apple-system, sans-serif;',
    '  font-size: 12px;',
    '  font-weight: 500;',
    '  letter-spacing: 0.02em;',
    '  background: var(--aegis-nav-bg, #f0f0f0);',
    '  border-bottom: 1px solid var(--aegis-nav-border, #d4d4d4);',
    '  color: var(--aegis-nav-text, #595959);',
    '  overflow-x: auto;',
    '  overflow-y: hidden;',
    '  scrollbar-width: none;',
    '}',
    '.aegis-nav::-webkit-scrollbar { display: none; }',

    /* Hub link (diamond + "AEGIS Initiative") */
    '.aegis-nav-hub {',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 6px;',
    '  text-decoration: none;',
    '  color: var(--aegis-nav-text, #595959);',
    '  flex-shrink: 0;',
    '  transition: color 0.15s;',
    '}',
    /* Diamond inherits color from the link */
    '.aegis-nav-hub svg { flex-shrink: 0; fill: currentColor; }',
    '.aegis-nav-hub:hover { color: var(--aegis-nav-accent, #0062a5); }',
    '.aegis-nav-hub:focus-visible {',
    '  outline: 2px solid var(--aegis-nav-accent, #0062a5);',
    '  outline-offset: 2px;',
    '  border-radius: 2px;',
    '}',
    '.aegis-nav-hub-text {',
    '  font-weight: 600;',
    '  font-size: 12px;',
    '  letter-spacing: 0.04em;',
    '}',
    /* Active state for hub */
    '.aegis-nav-hub[data-active="true"] {',
    '  color: var(--aegis-nav-accent, #0062a5);',
    '}',

    /* Vertical separator between hub and peer links */
    '.aegis-nav-sep {',
    '  width: 1px;',
    '  height: 14px;',
    '  background: var(--aegis-nav-border, #d4d4d4);',
    '  margin: 0 0.375rem 0 0.75rem;',
    '  flex-shrink: 0;',
    '}',

    /* Site links container */
    '.aegis-nav-links {',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 0;',
    '  flex-shrink: 0;',
    '}',

    /* Bullet separator between peer links */
    '.aegis-nav-dot {',
    '  color: var(--aegis-nav-muted, #aaaaaa);',
    '  font-size: 14px;',
    '  line-height: 1;',
    '  padding: 0 6px;',
    '  user-select: none;',
    '}',

    /* Individual site link */
    '.aegis-nav-link {',
    '  display: flex;',
    '  align-items: center;',
    '  padding: 3px 6px;',
    '  text-decoration: none;',
    '  color: var(--aegis-nav-text, #595959);',
    '  border-radius: 3px;',
    '  transition: color 0.15s, background 0.15s;',
    '  white-space: nowrap;',
    '  border-bottom: 1px solid transparent;',
    '}',
    '.aegis-nav-link:hover {',
    '  color: var(--aegis-nav-accent, #0062a5);',
    '  text-decoration: underline;',
    '  text-underline-offset: 2px;',
    '}',
    '.aegis-nav-link:focus-visible {',
    '  outline: 2px solid var(--aegis-nav-accent, #0062a5);',
    '  outline-offset: 2px;',
    '}',
    /* Active link: accent color + persistent underline */
    '.aegis-nav-link[data-active="true"] {',
    '  color: var(--aegis-nav-accent, #0062a5);',
    '  font-weight: 600;',
    '  text-decoration: underline;',
    '  text-underline-offset: 2px;',
    '  text-decoration-thickness: 2px;',
    '}',

    /* Mobile: hide hub text below 480, show just diamond */
    '@media (max-width: 480px) {',
    '  .aegis-nav-hub-text { display: none; }',
    '}',
  ].join('\n');

  // ── Diamond SVG — uses currentColor so it matches the text ─────────
  var DIAMOND_SVG = [
    '<svg width="14" height="16" viewBox="80 0 290 370" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
    '  <path fill="currentColor" d="m 225.0504,316.1296 -102.54,-131.09733 102.54,-131.09733 102.54,131.09733 z m 0,-316.1293254301 L 80.327737,185.03227 225.0504,370.06427 369.77306,185.03227 Z" />',
    '</svg>',
  ].join('');

  // ── Markup ─────────────────────────────────────────────────────────
  var nav = document.createElement('nav');
  nav.className = 'aegis-nav';
  nav.setAttribute('aria-label', 'AEGIS ecosystem navigation');

  // Hub link: diamond + "AEGIS Initiative"
  var hubLink = document.createElement('a');
  hubLink.className = 'aegis-nav-hub';
  hubLink.href = HUB_URL;
  hubLink.title = 'AEGIS Initiative — Ecosystem Home';
  if (activeSite === 'initiative') {
    hubLink.dataset.active = 'true';
    hubLink.setAttribute('aria-current', 'true');
  }
  hubLink.innerHTML = DIAMOND_SVG + '<span class="aegis-nav-hub-text">AEGIS Initiative</span>';
  nav.appendChild(hubLink);

  // Vertical separator
  var sep = document.createElement('div');
  sep.className = 'aegis-nav-sep';
  sep.setAttribute('role', 'separator');
  sep.setAttribute('aria-orientation', 'vertical');
  nav.appendChild(sep);

  // Peer site links with middot separators
  var linksWrap = document.createElement('div');
  linksWrap.className = 'aegis-nav-links';

  var visibleCount = 0;
  for (var j = 0; j < SITES.length; j++) {
    var site = SITES[j];
    if (!site.visible) continue;

    // Add middot separator before every link except the first
    if (visibleCount > 0) {
      var dot = document.createElement('span');
      dot.className = 'aegis-nav-dot';
      dot.setAttribute('aria-hidden', 'true');
      dot.textContent = '\u2022';
      linksWrap.appendChild(dot);
    }

    var a = document.createElement('a');
    a.className = 'aegis-nav-link';
    a.href = site.url;
    a.textContent = site.label;
    if (site.id === activeSite) {
      a.dataset.active = 'true';
      a.setAttribute('aria-current', 'true');
    }
    linksWrap.appendChild(a);
    visibleCount++;
  }

  nav.appendChild(linksWrap);

  // ── Assemble Shadow DOM ────────────────────────────────────────────
  shadow.appendChild(style);
  shadow.appendChild(nav);

  // ── Inject into page ───────────────────────────────────────────────
  document.body.insertBefore(host, document.body.firstChild);

  // Add top padding to body so content isn't hidden behind the fixed bar
  var existingPadding = parseInt(window.getComputedStyle(document.body).paddingTop, 10) || 0;
  document.body.style.paddingTop = (existingPadding + NAV_HEIGHT) + 'px';

  // ── Theme observer ─────────────────────────────────────────────────
  function syncTheme() {
    var theme = document.documentElement.dataset.theme || 'light';
    var isDark = theme === 'dark';
    nav.style.setProperty('--aegis-nav-bg',           isDark ? '#0a0a0a' : '#f0f0f0');
    nav.style.setProperty('--aegis-nav-border',        isDark ? '#2a2a2a' : '#d4d4d4');
    nav.style.setProperty('--aegis-nav-text',          isDark ? '#999999' : '#595959');
    nav.style.setProperty('--aegis-nav-accent',        isDark ? '#4da6f0' : '#0062a5');
    nav.style.setProperty('--aegis-nav-hover-bg',      isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)');
    nav.style.setProperty('--aegis-nav-muted',         isDark ? '#555555' : '#aaaaaa');
  }

  syncTheme();

  var observer = new MutationObserver(function (mutations) {
    for (var k = 0; k < mutations.length; k++) {
      if (mutations[k].attributeName === 'data-theme') {
        syncTheme();
        break;
      }
    }
  });

  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();
