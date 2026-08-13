/* Self-issued completion certificate.
 *
 * There is no server here and nothing is uploaded, so the honest framing is
 * "you completed this" rather than "we certify you". The page says so, and the
 * artwork says so on its face. A course about spotting inflated credentials has
 * no business minting one.
 *
 * The verification code is a short digest of name + score + date. It does not
 * prove anything on its own — it exists so that two copies of the same
 * certificate can be told apart, and so a listing in the repo can reference one.
 */
(function () {
  'use strict';

  var host = document.getElementById('cert');
  if (!host) return;

  var PASS = Number(host.getAttribute('data-pass') || 16);
  var TOTAL = Number(host.getAttribute('data-total') || 20);

  function digest(s) {
    // FNV-1a, rendered base36. Not cryptographic and not claimed to be.
    var h = 0x811c9dc5;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
    }
    return h.toString(36).toUpperCase().padStart(7, '0').slice(0, 7);
  }

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function draw(name, score, dateStr, code) {
    var W = 1200, H = 750, s = 2;           // 2x for a crisp download
    var c = document.createElement('canvas');
    c.width = W * s; c.height = H * s;
    var g = c.getContext('2d');
    g.scale(s, s);

    var ink = '#16181d', mut = '#697080', line = '#e0ddd6';
    var bio = '#2e3f8c', code_c = '#1c6b58', warn = '#a8382c';

    g.fillStyle = '#fffefc'; g.fillRect(0, 0, W, H);
    // the two-tone rail: the same mark the site uses
    var grd = g.createLinearGradient(0, 0, 0, H);
    grd.addColorStop(0, bio); grd.addColorStop(0.5, bio);
    grd.addColorStop(0.5, code_c); grd.addColorStop(1, code_c);
    g.fillStyle = grd; g.fillRect(0, 0, 16, H);

    g.strokeStyle = line; g.lineWidth = 1;
    g.strokeRect(48.5, 40.5, W - 96, H - 80);

    var L = 96;
    g.fillStyle = warn;
    g.font = '600 15px ui-monospace, Menlo, monospace';
    g.fillText('结 业 证 明   ·   C O U R S E   C O M P L E T I O N', L, 122);

    g.fillStyle = ink;
    g.font = '700 40px -apple-system, "PingFang SC", sans-serif';
    g.fillText('抗体与蛋白数据 × AI for Science', L, 190);
    g.font = '700 34px -apple-system, "PingFang SC", sans-serif';
    g.fillText('程序员两天速成营', L, 240);

    g.strokeStyle = line; g.beginPath(); g.moveTo(L, 282); g.lineTo(W - 96, 282); g.stroke();

    g.fillStyle = mut;
    g.font = '15px -apple-system, "PingFang SC", sans-serif';
    g.fillText('兹证明以下学习者已完成全部八节课程并通过结业考试', L, 322);

    g.fillStyle = ink;
    g.font = '700 54px -apple-system, "PingFang SC", sans-serif';
    g.fillText(name, L, 400);

    // score / date / code, on one baseline
    var cols = [
      ['结业考试得分', score + ' / ' + TOTAL],
      ['完成日期', dateStr],
      ['证明编号', code]
    ];
    var x = L;
    cols.forEach(function (col) {
      g.fillStyle = mut;
      g.font = '13px -apple-system, "PingFang SC", sans-serif';
      g.fillText(col[0], x, 470);
      g.fillStyle = ink;
      g.font = '600 22px ui-monospace, Menlo, monospace';
      g.fillText(col[1], x, 502);
      x += 260;
    });

    // The disclaimer is part of the artwork on purpose — it travels with the
    // image, so the certificate cannot be screenshotted free of its own caveat.
    g.fillStyle = mut;
    g.font = '13px -apple-system, "PingFang SC", sans-serif';
    g.fillText('本证明由学习者本人在浏览器中自助生成，未经第三方核验，不构成任何资质认证。', L, 606);
    g.fillText('它证明的是「完成了这套公开材料」，课程内容与实验代码均开源可查。', L, 630);

    g.fillStyle = ink;
    g.font = '700 19px ui-monospace, Menlo, monospace';
    g.fillText('AI4S', L, 686);
    g.fillStyle = mut;
    g.font = '14px ui-monospace, Menlo, monospace';
    g.fillText('ai4s.runixcloud.io', L + 62, 686);

    return c;
  }

  var nameInput = host.querySelector('#certname');
  var out = host.querySelector('#certout');
  var dl = host.querySelector('#certdl');
  var meta = host.querySelector('#certmeta');
  var current = null;

  function render() {
    var name = (nameInput.value || '').trim().slice(0, 24);
    if (!name) { out.innerHTML = '<p class="hint">填入名字后即可生成。</p>'; dl.hidden = true; return; }
    var score = Number(host.getAttribute('data-score') || 0);
    var d = new Date();
    var dateStr = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') +
                  '-' + String(d.getDate()).padStart(2, '0');
    var code = digest(name + '|' + score + '|' + dateStr);
    current = draw(name, score, dateStr, code);
    out.innerHTML = '';
    current.style.width = '100%';
    current.style.height = 'auto';
    current.style.borderRadius = '10px';
    current.style.border = '1px solid var(--line)';
    out.appendChild(current);
    dl.hidden = false;
    meta.textContent = '证明编号 ' + code + ' · ' + dateStr;
    host.setAttribute('data-code', code);
    host.setAttribute('data-date', dateStr);
  }

  nameInput.addEventListener('input', render);
  dl.addEventListener('click', function () {
    if (!current) return;
    var a = document.createElement('a');
    a.download = 'ai4s-completion-' + (host.getAttribute('data-code') || 'cert') + '.png';
    a.href = current.toDataURL('image/png');
    a.click();
  });

  // Unlocked by the exam; also reachable directly for anyone who already passed.
  window.__ai4sUnlockCert = function (score) {
    host.setAttribute('data-score', String(score));
    host.hidden = false;
    var gate = document.getElementById('certgate');
    if (gate) gate.hidden = true;
    render();
    host.scrollIntoView({ block: 'start', behavior: 'smooth' });
  };
  host.__pass = PASS;
})();
