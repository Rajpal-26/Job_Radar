/* Injects the shared left rail. Set <body data-nav="01-wallet"> */
(function () {
  var I = {
    wallet: '<path d="M3 7h15a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 7l12-3v3"/><circle cx="16" cy="13" r="1.3"/>',
    buckets: '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    plans: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/>',
    topup: '<circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/>',
    checkout: '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M3 4h2l2.4 11h11.2l2-8H6.2"/>',
    spend: '<path d="M13 3L4 14h6l-1 7 9-11h-6z"/>',
    ledger: '<path d="M4 6h16M4 12h16M4 18h10"/>',
    receipt: '<path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 7h6M9 11h6"/>',
    low: '<path d="M12 3l9 16H3z"/><path d="M12 9v5M12 17h.01"/>'
  };
  var NAV = [
    { grp: 'Wallet' },
    { id: '01-wallet', href: '01-wallet.html', label: 'Wallet &amp; credits', i: 'wallet' },
    { id: '02-buckets', href: '02-buckets.html', label: 'Buckets &amp; expiry', i: 'buckets' },
    { grp: 'Get credits' },
    { id: '03-plans', href: '03-plans.html', label: 'Plans &amp; pricing', i: 'plans' },
    { id: '04-topup', href: '04-topup.html', label: 'Top-up packs', i: 'topup' },
    { id: '05-checkout', href: '05-checkout.html', label: 'Checkout', i: 'checkout' },
    { grp: 'Use credits' },
    { id: '06-spend', href: '06-spend.html', label: 'Spend a credit', i: 'spend' },
    { id: '07-ledger', href: '07-ledger.html', label: 'Ledger', i: 'ledger' },
    { id: '08-receipt', href: '08-receipt.html', label: 'Receipt', i: 'receipt' },
    { id: '09-lowcredit', href: '09-lowcredit.html', label: 'Low credit', i: 'low', tag: '!' }
  ];
  var active = (document.body && document.body.dataset.nav) || location.pathname.replace(/\\/g, '/').split('/').pop().replace('.html', '');

  var html = '<div class="brand"><span class="mark">JR</span> Job Radar</div>' +
    '<nav class="nav">';
  NAV.forEach(function (n) {
    if (n.grp) { html += '<div class="grp">' + n.grp + '</div>'; return; }
    var on = n.id === active ? ' class="on"' : '';
    html += '<a' + on + ' href="' + n.href + '">' +
      '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + I[n.i] + '</svg>' +
      n.label + (n.tag ? ' <span class="tag">' + n.tag + '</span>' : '') + '</a>';
  });
  html += '</nav>' +
    '<div class="balance-mini"><div class="lbl">Credits left</div>' +
    '<div class="val"><b data-count="142">0</b><small>cr · Pro</small></div></div>';

  var host = document.querySelector('[data-rail]');
  if (host) { host.innerHTML = html; host.classList.add('rail'); }
})();
