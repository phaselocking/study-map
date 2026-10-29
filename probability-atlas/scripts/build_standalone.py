"""Build a self-contained archive HTML, with readable content even without JS."""
import argparse
import base64
import html
import json
import mimetypes
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def esc(value):
    return html.escape(str(value or ''), quote=True)

def build(root, output):
    lessons = json.loads((root / 'data/lessons.json').read_text(encoding='utf-8'))
    concepts = json.loads((root / 'data/concepts.json').read_text(encoding='utf-8'))
    transcripts = {l['id']: json.loads((root / l['transcriptPath']).read_text(encoding='utf-8')) for l in lessons['lessons']}
    files = {}
    for p in (root / 'sources').rglob('*'):
        if p.is_file():
            mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
            if p.suffix in ('.txt', '.md'):
                mime = 'text/plain;charset=utf-8'
            files[p.relative_to(root).as_posix()] = {'mime': mime, 'base64': base64.b64encode(p.read_bytes()).decode()}
    payload = json.dumps({'lessons': lessons, 'concepts': concepts, 'transcripts': transcripts, 'files': files}, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    katex_css = (root / 'vendor/katex/katex.min.css').read_text(encoding='utf-8')
    # Use the compact WOFF2 variant; no font URL may remain external.
    def font_src(match):
        value = match.group(1)
        font = re.search(r'url\(([^)]+\.woff2)\)', value)
        if not font:
            return match.group(0)
        path = font.group(1).strip('\"\'')
        data = base64.b64encode((root / 'vendor/katex' / path).read_bytes()).decode()
        return 'src:url(data:font/woff2;base64,' + data + ') format("woff2")'
    katex_css = re.sub(r'src:([^;]+)', font_src, katex_css)
    css = (root / 'styles.css').read_text(encoding='utf-8')
    app = (root / 'app.js').read_text(encoding='utf-8')
    app = app.replace("const latest=lessons.at(-1)", "const latest=lessons[lessons.length-1]")
    old_path = "const safePath = path => typeof path === 'string' && /^(sources|data)\\//.test(path) && !path.split('/').includes('..') ? path.split('/').map(encodeURIComponent).join('/') : null;"
    new_path = """const standalone = JSON.parse(document.getElementById('archive-payload').textContent);
  const fileUrls = new Map();
  const safePath = path => {
    if(typeof path!=='string' || !/^(sources|data)\\//.test(path) || path.split('/').includes('..'))return null;
    if(standalone.files[path]){
      if(!fileUrls.has(path)){
        const file=standalone.files[path], binary=atob(file.base64), bytes=new Uint8Array(binary.length);
        for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
        fileUrls.set(path,URL.createObjectURL(new Blob([bytes],{type:file.mime})));
      }
      return fileUrls.get(path);
    }
    return null;
  };"""
    assert old_path in app, 'Source-path adapter changed; review builder'
    app = app.replace(old_path, new_path)
    old_fetch = "const response=await fetch(path);if(!response.ok)throw new Error('转录文件无法读取');transcriptCache.set(id,await response.json());"
    assert old_fetch in app
    app = app.replace("const path=safePath(lesson.transcriptPath);if(!path)throw new Error('无效转录路径');"+old_fetch,
                      "const content=standalone.transcripts[id];if(!content)throw new Error('未收录转录');transcriptCache.set(id,content);")
    old_init = "const results=await Promise.all(['data/lessons.json','data/concepts.json'].map(async path=>{const r=await fetch(path);if(!r.ok)throw new Error('无法读取 '+path);return r.json();}));"
    assert old_init in app
    app = app.replace(old_init, 'const results=[standalone.lessons,standalone.concepts];')
    assert 'fetch(' not in app, 'Standalone must not request files'
    types = lessons['sourceTypes']
    labels = {'outline':'课堂脉络','explanations':'重点讲解','examples':'例题','examTips':'考试提示','personalNotes':'我的学习记录','connections':'知识联系'}
    rows = []
    menu = []
    # This is real reading content, not a JS-only loading placeholder.
    for lesson in reversed(lessons['lessons']):
        lid = lesson['id']
        menu.append(f'<li><a href="#offline-{lid}">{esc(lesson["date"])} · {esc(lesson["title"])}</a></li>')
        chunks = [f'<article id="offline-{lid}" class="offline-lesson"><header class="lesson-header"><div class="eyebrow">{lid}</div><h2>{esc(lesson["title"])}</h2><p>{esc(lesson["summary"])}</p></header>']
        if lesson.get('recording', {}).get('missingOpeningSeconds'):
            chunks.append('<p class="notice">开头约5分钟未录到。以下使用录音文件内的原时间戳。</p>')
        for key, label in labels.items():
            cards = lesson['sections'].get(key, [])
            chunks.append(f'<section class="detail-section"><h2>{label}</h2>')
            if not cards:
                chunks.append('<p class="section-empty">现有材料暂无有依据的记录。</p>')
            for card in cards:
                chunks.append(f'<article class="evidence-card"><span class="source-badge {esc(card["sourceType"])}">{esc(types[card["sourceType"]])}</span><h3>{esc(card["title"])}</h3><p class="card-text">{esc(card["text"])}</p>')
                if card.get('formula'):
                    chunks.append(f'<pre class="formula">{esc(card["formula"])}</pre>')
                if card.get('caution'):
                    chunks.append(f'<aside class="notice">{esc(card["caution"])}</aside>')
                for ref in card.get('sources', []):
                    source = next(s for s in lesson['sources'] if s['id'] == ref['sourceId'])
                    stamp = ref.get('timestamp')
                    if stamp:
                        paragraph = next((b for b in transcripts[lid]['blocks'] if b['timestamp'] == stamp), None)
                        if paragraph:
                            chunks.append(f'<a class="timestamp" href="#offline-{lid}-{paragraph["id"]}">{stamp}</a> ')
                    chunks.append(f'<small>{esc(source["label"])}{(" · PDF第"+str(ref["page"])+"页") if ref.get("page") else ""}</small> ')
                chunks.append('</article>')
            chunks.append('</section>')
        chunks.append('<details><summary>逐段阅读原始转录</summary>')
        for block in transcripts[lid]['blocks']:
            chunks.append(f'<article id="offline-{lid}-{block["id"]}" class="transcript-block"><div class="block-meta">{esc(block["timestamp"])} · {esc(block["speaker"])}</div><p>{esc(block["text"])}</p></article>')
        chunks.append('</details></article>')
        rows.append(''.join(chunks))
    lesson_count = len(lessons['lessons'])
    paragraph_count = sum(len(t['blocks']) for t in transcripts.values())
    fallback = '<header class="page-intro"><div class="eyebrow">Probability Archive · 单文件阅读版</div><h1>概率论课堂档案馆</h1><p>'+str(lesson_count)+'次真实课堂，含'+str(paragraph_count)+'段转录。无需服务器或网络。支持脚本时可搜索与导航；预览器未运行脚本时，下方仍可直接阅读。</p><p>课件与原文已嵌入，支持脚本后可打开来源副本。</p></header><ol class="offline-menu">'+''.join(menu)+'</ol>'+''.join(rows)
    template = (root / 'index.html').read_text(encoding='utf-8')
    template = re.sub(r'<link rel="stylesheet" href="[^"]+">', '', template)
    template = re.sub(r'<script defer src="[^"]+"></script>', '', template)
    license_text = (root / 'vendor/katex/LICENSE').read_text(encoding='utf-8')
    template = template.replace('</head>', '<!-- Bundled KaTeX license\n'+license_text.replace('--', '—')+'\n--><style>'+katex_css+'\n'+css+'\n.offline-lesson{margin:48px 0 80px}.offline-menu{line-height:2.3}.offline-lesson pre{white-space:pre-wrap}.offline-lesson small{color:var(--muted)}\n</style></head>')
    template = re.sub(r'<main id="main" tabindex="-1">.*?</main>', lambda m:'<main id="main" tabindex="-1">'+fallback+'</main>', template, flags=re.S)
    template = re.sub(r'<noscript>.*?</noscript>', '', template, flags=re.S)
    scripts = [f'<script type="application/json" id="archive-payload">{payload}</script>']
    for source in ('vendor/katex/katex.min.js', 'vendor/katex/contrib/auto-render.min.js'):
        js = (root / source).read_text(encoding='utf-8').replace('</script', '<\\/script')
        scripts.append('<script>'+js+'</script>')
    scripts.append('<script>'+app.replace('</script', '<\\/script')+'</script>')
    template = template.replace('</body>', '\n'.join(scripts)+'\n</body>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template, encoding='utf-8')
    print(json.dumps({'file':str(output.resolve()), 'bytes':output.stat().st_size, 'lessons':len(lessons['lessons']), 'paragraphs':sum(len(t['blocks']) for t in transcripts.values()), 'embeddedSourceFiles':len(files)},ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'probability-archive.html')
    args = parser.parse_args()
    build(args.root.resolve(), args.output.resolve())
