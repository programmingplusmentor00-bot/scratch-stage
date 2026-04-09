<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>作品プレイヤー</title>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Kosugi+Maru&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Kosugi Maru', sans-serif;
      background: #1a1a2e;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: linear-gradient(135deg, #667eea, #764ba2);
      padding: 14px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .back-btn {
      background: rgba(255,255,255,0.2);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 8px 16px;
      font-family: 'Kosugi Maru', sans-serif;
      font-size: 14px;
      cursor: pointer;
      text-decoration: none;
      transition: background 0.2s;
    }
    .back-btn:hover { background: rgba(255,255,255,0.35); }
    .header-info { flex: 1; }
    .header-info h1 {
      font-family: 'Nunito', sans-serif;
      font-weight: 900;
      font-size: 20px;
      color: white;
    }
    .header-info p { font-size: 13px; color: rgba(255,255,255,0.75); margin-top: 2px; }
    .player-wrap {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .player-container {
      width: 100%;
      max-width: 800px;
      background: #000;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 24px 60px rgba(0,0,0,0.5);
      aspect-ratio: 16/9;
      position: relative;
    }
    iframe {
      width: 100%;
      height: 100%;
      border: none;
      display: block;
    }
    .loading {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #1a1a2e;
      color: white;
      gap: 16px;
      font-size: 18px;
    }
    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid rgba(255,255,255,0.2);
      border-top-color: #C77DFF;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    .error {
      position: absolute;
      inset: 0;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #1a1a2e;
      color: #ff6b6b;
      gap: 16px;
      font-size: 16px;
      padding: 24px;
      text-align: center;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

<header>
  <a class="back-btn" href="javascript:history.back()">← もどる</a>
  <div class="header-info">
    <h1 id="work-title">よみこみちゅう…</h1>
    <p id="work-author"></p>
  </div>
</header>

<div class="player-wrap">
  <div class="player-container">
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <span>よみこみちゅう…</span>
    </div>
    <div class="error" id="error">
      <span style="font-size:48px">😢</span>
      <span id="error-msg">よみこみに失敗しました</span>
    </div>
    <iframe id="player" allow="autoplay; fullscreen"></iframe>
  </div>
</div>

<script>
  const params = new URLSearchParams(location.search);
  const file   = params.get('file');
  const title  = params.get('title') || '作品';
  const author = params.get('author') || '';

  document.title = title + ' - スクラッチギャラリー';
  document.getElementById('work-title').textContent = title;
  if (author) document.getElementById('work-author').textContent = '✏️ ' + author;

  async function loadSb3() {
    if (!file) return showError('ファイルが指定されていません');

    try {
      // sb3ファイルをfetchして ArrayBuffer で取得
      const res = await fetch(file);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buf = await res.arrayBuffer();

      // ArrayBuffer → base64
      const bytes = new Uint8Array(buf);
      let binary = '';
      for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      const base64 = btoa(binary);
      const dataUrl = 'data:application/zip;base64,' + base64;

      // TurboWarp Packager の embed URL に dataURL を渡す
      const playerUrl = `https://turbowarp.org/embed#project=${encodeURIComponent(dataUrl)}`;
      const iframe = document.getElementById('player');
      iframe.src = playerUrl;
      iframe.onload = () => {
        document.getElementById('loading').style.display = 'none';
      };
    } catch (e) {
      showError('ファイルの読み込みに失敗しました: ' + e.message);
    }
  }

  function showError(msg) {
    document.getElementById('loading').style.display = 'none';
    const el = document.getElementById('error');
    el.style.display = 'flex';
    document.getElementById('error-msg').textContent = msg;
  }

  loadSb3();
</script>
</body>
</html>
