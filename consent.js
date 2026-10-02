/*
 * Loads Google Analytics only after the visitor accepts, and never before.
 * The choice is kept in localStorage and can be changed from the footer at any time.
 */
(function () {
  var STORAGE_KEY = 'philjay-analytics-consent';
  var MEASUREMENT_ID = 'G-9EDNTGFEM7';
  var banner = null;
  var TEXT = document.documentElement.lang.indexOf('de') === 0 ? {
    label: 'Cookie-Hinweis',
    message: 'Diese Seite würde Besuche gerne mit Google Analytics zählen, das Cookies in deinem Browser speichert. ' +
      'Es läuft nur, wenn du zustimmst, und bis dahin wird nichts gemessen. ',
    link: 'Was erfasst wird',
    privacy: '/de/datenschutz.html',
    decline: 'Ablehnen',
    allow: 'Erlauben'
  } : {
    label: 'Cookie notice',
    message: 'This site would like to count visits with Google Analytics, which stores cookies in your browser. ' +
      'It runs only if you allow it, and nothing is measured until you do. ',
    link: 'What is collected',
    privacy: '/privacy.html',
    decline: 'Decline',
    allow: 'Allow'
  };

  function stored() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      return null;
    }
  }

  function remember(choice) {
    try {
      window.localStorage.setItem(STORAGE_KEY, choice);
    } catch (error) {
      // A browser with storage blocked simply asks again next time.
    }
  }

  function startAnalytics() {
    if (window.__analyticsStarted) return;
    window.__analyticsStarted = true;

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', MEASUREMENT_ID);

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    document.head.appendChild(script);
  }

  function clearAnalyticsCookies() {
    var names = document.cookie.split(';').map(function (pair) { return pair.split('=')[0].trim(); });
    names.forEach(function (name) {
      if (name.indexOf('_ga') !== 0) return;
      var expiry = '; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
      document.cookie = name + '=' + expiry;
      document.cookie = name + '=' + expiry + '; domain=.' + window.location.hostname;
    });
  }

  function hide() {
    if (!banner) return;
    banner.remove();
    banner = null;
  }

  function choose(choice) {
    remember(choice);
    hide();
    if (choice === 'granted') startAnalytics();
    else clearAnalyticsCookies();
  }

  function show() {
    if (banner) return;
    banner = document.createElement('div');
    banner.className = 'consent';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', TEXT.label);
    banner.innerHTML =
      '<p>' + TEXT.message + '<a href="' + TEXT.privacy + '">' + TEXT.link + '</a>.</p>' +
      '<div class="consent-actions">' +
      '<button type="button" class="button" data-choice="denied">' + TEXT.decline + '</button>' +
      '<button type="button" class="button primary" data-choice="granted">' + TEXT.allow + '</button>' +
      '</div>';
    banner.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-choice]');
      if (button) choose(button.getAttribute('data-choice'));
    });
    document.body.appendChild(banner);
  }

  // Changing your mind: any element with data-cookie-settings reopens the question.
  document.addEventListener('click', function (event) {
    var trigger = event.target.closest('[data-cookie-settings]');
    if (!trigger) return;
    event.preventDefault();
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      // Nothing to remove.
    }
    show();
  });

  var choice = stored();
  if (choice === 'granted') startAnalytics();
  else if (choice !== 'denied') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show);
    else show();
  }
})();
