'use strict';
(() => {
  const main = document.querySelector('main');
  const types = {teacher_quote:'老师原话', transcript_summary:'转录摘要', ai_analysis:'整理分析', personal_record:'个人自述'};
  const labels = {outline:'课堂脉络',explanations:'重点讲解',examples:'课堂例题',examTips:'考试提示',personalNotes:'我的学习记录',connections:'知识联系',sources:'原始资料'};
  const filter = {q:'',date:'',concept:'',emphasis:false};
  const transcriptCache = new Map();
  let lessons = [], concepts = [], course = {}, generation = 0;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safePath = path => typeof path === 'string' && /^(sources|data)\//.test(path) && !path.split('/').includes('..') ? path.split('/').map(encodeURIComponent).join('/') : null;
  const lessonUrl = (id, t) => '#/lesson/' + encodeURIComponent(id) + (t ? '?t=' + encodeURIComponent(t) : '');
  const conceptUrl = id => '#/concept/' + encodeURIComponent(id);
  const findConcept = id => concepts.find(c => c.id === id);
  const dateParts = date => ({year: String(date).slice(0,4),short:String(date).slice(5).replace('-','.')});
  const cardsOf = l => Object.values(l.sections || {}).flat().filter(x => x && typeof x === 'object');
  const emphasisCards = l => [...(l.sections?.examTips || []), ...cardsOf(l).filter(c => c.emphasis || c.emphasized)];
  const searchable = l => [l.date,l.title,l.summary,...(l.conceptIds || []).flatMap(id=>{const c=findConcept(id);return c ? [c.name,...(c.aliases || [])] : [id];}),...cardsOf(l).flatMap(c=>[c.title,c.text,c.formula])].join(' ').toLocaleLowerCase();
  const matches = l => {
    if (filter.date && l.date !== filter.date) return false;
    if (filter.concept && !(l.conceptIds || []).includes(filter.concept)) return false;
    if (filter.emphasis && emphasisCards(l).length === 0) return false;
    const words = filter.q.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const text = filter.emphasis ? [l.date,l.title,...emphasisCards(l).flatMap(c=>[c.title,c.text])].join(' ').toLocaleLowerCase() : searchable(l);
    return words.every(w => text.includes(w));
  };
  const pills = ids => (ids || []).map(id => {const c=findConcept(id);return c ? `<a class="concept-pill" href="${conceptUrl(id)}">${escape(c.name)}</a>` : '';}).join('');
  const badge = type => `<span class="source-badge ${escape(type)}">${escape(types[type] || '来源待核')}</span>`;
  function lessonRows(list) {
    if (!list.length) return '<div class="empty-state"><strong>这一页，暂时没有匹配的档案。</strong>试试减少关键词，或清除日期与知识点筛选。</div>';
    return list.map(l => {const d=dateParts(l.date);const index=lessons.findIndex(x=>x.id===l.id)+1;return `<article class="archive-row"><div class="archive-date">${escape(d.short)}<small>${escape(d.year)}</small></div><div class="archive-main"><span class="archive-number">CLASS ${String(index).padStart(2,'0')} ${l.coverage==='detailed'?'<span class="coverage-tag">完整示范档案</span>':''}</span><h3><a href="${lessonUrl(l.id)}">${escape(l.title)}</a></h3><p>${escape(l.summary || '已收录原始课堂资料，结构化整理待补充。')}</p><div class="archive-tags">${pills(l.conceptIds)}</div></div><a class="archive-arrow" href="${lessonUrl(l.id)}" aria-label="查阅${escape(l.date)}课堂">↗</a></article>`;}).join('');
  }
  function filterBar() {
    return `<form class="filter-bar" id="archive-filter" role="search"><label class="search-field"><span class="field-label">检索档案 / SEARCH</span><input type="search" class="search-input" id="keyword" placeholder="输入关键词、日期或讲解内容" value="${escape(filter.q)}" autocomplete="off"></label><label><span class="field-label">课堂日期</span><select class="filter-select" id="date-filter"><option value="">全部日期</option>${lessons.map(l=>`<option value="${escape(l.date)}" ${filter.date===l.date?'selected':''}>${escape(l.date)}</option>`).join('')}</select></label><label><span class="field-label">知识主题</span><select class="filter-select" id="concept-filter"><option value="">全部知识点</option>${concepts.map(c=>`<option value="${escape(c.id)}" ${filter.concept===c.id?'selected':''}>${escape(c.name)}</option>`).join('')}</select></label></form><div class="filter-options"><label class="check-label"><input type="checkbox" id="emphasis-filter" ${filter.emphasis?'checked':''}>只看老师强调 / 考试提示</label><button class="clear-button" id="clear-filter" type="button">清除筛选 ↺</button></div><div id="filter-results" aria-live="polite"></div>`;
  }
  function bindFilters() {
    const form=document.querySelector('#archive-filter');
    if (!form) return;
    form.addEventListener('submit', e=>e.preventDefault());
    document.querySelector('#keyword').addEventListener('input',e=>{filter.q=e.target.value;renderResults();});
    document.querySelector('#date-filter').addEventListener('change',e=>{filter.date=e.target.value;renderResults();});
    document.querySelector('#concept-filter').addEventListener('change',e=>{filter.concept=e.target.value;renderResults();});
    document.querySelector('#emphasis-filter').addEventListener('change',e=>{filter.emphasis=e.target.checked;renderResults();});
    document.querySelector('#clear-filter').addEventListener('click',()=>{Object.assign(filter,{q:'',date:'',concept:'',emphasis:false});form.reset();document.querySelector('#keyword').value='';document.querySelector('#date-filter').value='';document.querySelector('#concept-filter').value='';document.querySelector('#emphasis-filter').checked=false;renderResults();});
    renderResults();
  }
  function renderResults() {
    const target=document.querySelector('#filter-results');if(!target)return;
    const list=lessons.filter(matches);
    target.innerHTML=`<p class="result-count">${list.length} / ${lessons.length} 份课堂档案 · 按授课日期排列</p>${lessonRows(list)}`;
  }
  function home() {
    const latest=lessons.at(-1);const d=latest ? dateParts(latest.date):null;
    main.innerHTML=`<section class="hero"><div><div class="eyebrow">A living record of the classroom</div><h1>在时间里，<br>读懂<em>概率</em>。</h1><p class="hero-intro">从一堂真实的课出发，留下讲解的脉络、例题的来处，以及知识彼此连接的时刻。</p><p class="hero-note">${escape(course.semester || '2026 秋季学期')} · ${escape(course.title || '概率论与数理统计')}</p></div>${latest?`<article class="featured"><div class="featured-label"><span>最新入藏 / LATEST ENTRY</span><span>NO. ${String(lessons.length).padStart(2,'0')}</span></div><div class="featured-date">${escape(d.short)}<span>${escape(d.year)} · 课堂记录</span></div><h2>${escape(latest.title)}</h2><p>${escape(latest.summary)}</p><a class="text-link" href="${lessonUrl(latest.id)}">翻开这堂课 <span aria-hidden="true">↗</span></a></article>`:''}</section><section class="stats" aria-label="馆藏概览"><div class="stat"><span class="stat-label">已收录课堂 / LESSONS</span><div class="stat-value">${lessons.length}<small>次真实课堂</small></div></div><div class="stat"><span class="stat-label">知识索引 / CONCEPTS</span><div class="stat-value">${concepts.length}<small>个可追溯主题</small></div></div><div class="stat"><span class="stat-label">课程进度 / PROGRESS</span><p class="stat-progress">${escape(course.progress?.label || '依据课堂资料持续更新')}</p><span class="stat-caption">截至 ${escape(course.progress?.asOf || latest?.date || '现有资料')} · 按实际讲授记录，非掌握程度</span></div></section><section><div class="section-heading"><h2>最近的知识主题<small>RECENT THEMES</small></h2><a href="#/concepts">查看索引 ↗</a></div><div class="recent-topics">${pills([...new Set(lessons.slice(-2).flatMap(l=>l.conceptIds || []))])}</div></section><section><div class="section-heading"><h2>课堂档案<small>THE CLASSROOM COLLECTION</small></h2><span class="stat-caption">真实记录 · 来源可查</span></div>${filterBar()}</section>`;
    bindFilters();
  }
  function timeline() {
    main.innerHTML=`<header class="page-intro"><div class="eyebrow">The classroom, in time</div><h1>课堂时间线</h1><p>沿实际授课顺序查阅。保留课堂里的展开、回看与修正，也保留资料尚未覆盖的空白。</p></header>${filterBar()}`;bindFilters();
  }
  function conceptIndex() {
    main.innerHTML=`<header class="page-intro"><div class="eyebrow">Ideas, connected</div><h1>知识索引</h1><p>一个概念，可以在不止一堂课中出现。从知识点回到课堂，区分实际讲授的联系与后续整理分析。</p></header><label class="concept-search"><span class="field-label" style="margin-top:24px">检索知识点</span><input type="search" class="search-input" id="concept-keyword" placeholder="例如 CDF、独立性、等待时间"></label><div id="concept-results" aria-live="polite"></div>`;
    const render=q=>{const list=concepts.filter(c=>[c.name,c.description,...(c.aliases||[])].join(' ').toLocaleLowerCase().includes(q.toLocaleLowerCase()));document.querySelector('#concept-results').innerHTML=`<p class="result-count">${list.length} 个知识主题</p><div class="concept-grid">${list.map(c=>`<a class="concept-card" href="${conceptUrl(c.id)}"><span class="index-number">INDEX ${String(concepts.indexOf(c)+1).padStart(2,'0')}</span><h2>${escape(c.name)}</h2><p>${escape(c.description || '')}</p><span class="card-foot">${(c.lessonIds||[]).length} 次相关课堂 <span aria-hidden="true">↗</span></span></a>`).join('')}</div>${!list.length?'<div class="empty-state">没有匹配的知识主题。</div>':''}`;};
    render('');document.querySelector('#concept-keyword').addEventListener('input',e=>render(e.target.value));
  }
  function conceptDetail(id) {
    const c=findConcept(id);if(!c)return notFound('没有找到这个知识主题。');
    main.innerHTML=`<div class="breadcrumb"><a href="#/concepts">知识索引</a><span>/</span><span>${escape(c.name)}</span></div><header class="page-intro" style="padding-top:0"><div class="eyebrow">Concept dossier</div><h1>${escape(c.name)}</h1><p>${escape(c.description || '')}</p>${(c.aliases||[]).length?`<p class="source-help">亦见：${escape(c.aliases.join(' / '))}</p>`:''}</header>${(c.relations||[]).length?`<section><div class="section-heading"><h2>知识之间的联系</h2></div><div class="relation-list">${c.relations.map(r=>{const other=findConcept(r.targetId);return `<article class="relation"><span class="source-badge ${r.type==='classroom'?'transcript_summary':'ai_analysis'}">${r.type==='classroom'?'课堂讲授关系':'整理分析'}</span> <a href="${conceptUrl(r.targetId)}">${escape(other?.name || r.targetId)} ↗</a><p>${escape(r.text)}</p><div class="citations">${(r.sources||[]).map(s=>{const l=lessons.find(x=>x.id===s.lessonId);return l?`<a href="${lessonUrl(l.id,s.timestamp)}">${escape(l.date)} ${escape(s.timestamp || '课堂档案')}</a>`:'';}).join('')}</div></article>`;}).join('')}</div></section>`:''}<div class="section-heading"><h2>相关课堂<small>BACK TO THE CLASSROOM</small></h2></div>${lessonRows(lessons.filter(l=>(c.lessonIds||[]).includes(l.id)))}`;
  }
  function citations(card,lesson) {
    return (card.sources||[]).map(ref=>{const source=(lesson.sources||[]).find(s=>s.id===ref.sourceId);const path=safePath(source?.path);const label=source?.label || ref.sourceId || '来源待核';return `${ref.timestamp?`<a class="timestamp" href="${lessonUrl(lesson.id,ref.timestamp)}" aria-label="定位原文 ${escape(ref.timestamp)}">${escape(ref.timestamp)}</a>`:''}${path?`<a href="${path}${ref.page?'#page='+encodeURIComponent(ref.page):''}" target="_blank" rel="noopener">${escape(label)}${ref.page?' · PDF第'+escape(ref.page)+'页':''}${ref.line?' · 第'+escape(ref.line)+'行':''} ↗</a>`:`<span>${escape(label)}</span>`}`;}).join('');
  }
  function section(key,lesson,index) {
    const list=lesson.sections?.[key] || [];
    const empty={outline:'这节课的课堂结构尚未整理，原始转录可在下方查阅。',explanations:'目前没有可单独确认的重点讲解条目。',examples:'目前没有可核实题设的例题条目。',examTips:'现有材料中未整理出可确认的考试提示。',personalNotes:'尚无有依据的个人学习记录。',connections:'尚未整理有证据的跨知识联系。'};
    return `<section class="detail-section" id="section-${key}"><h2><span>${String(index+1).padStart(2,'0')}</span>${labels[key]}</h2>${list.length?list.map(card=>`<article class="evidence-card" id="card-${escape(card.id)}"><div class="evidence-head">${badge(card.sourceType)}${key==='examTips'?'<span class="explicit-badge">课堂考试提示 · 非官方考纲</span>':(card.emphasis || card.emphasized)?'<span class="explicit-badge">老师明确强调</span>':''}</div><h3>${escape(card.title)}</h3><p class="card-text">${escape(card.text || '')}</p>${card.formula?`<div class="formula">\\[${escape(card.formula)}\\]</div>`:''}${card.caution?`<aside class="notice">${escape(card.caution)}</aside>`:''}<div class="citations">${citations(card,lesson)}</div></article>`).join(''):`<p class="section-empty">${empty[key]}</p>`}</section>`;
  }
  async function lessonDetail(id,query,currentGeneration) {
    const lesson=lessons.find(l=>l.id===id);if(!lesson)return notFound('没有找到这份课堂档案。');
    const keys=['outline','explanations','examples','examTips','personalNotes','connections'];const index=lessons.indexOf(lesson);const missing=lesson.recording?.missingOpeningSeconds;const t=query.get('t');
    document.title=lesson.date+' · '+lesson.title+'｜Probability Archive';
    main.innerHTML=`<div class="breadcrumb"><a href="#/timeline">课堂时间线</a><span>/</span><span>${escape(lesson.date)}</span></div><header class="lesson-header"><div class="lesson-meta"><span>CLASS ${String(index+1).padStart(2,'0')}</span><span>${escape(lesson.date)}</span><span>${lesson.coverage==='detailed'?'完整示范档案':'基础勘察档案'}</span></div><h1>${escape(lesson.title)}</h1><p class="lesson-summary">${escape(lesson.summary || '')}</p><div class="archive-tags">${pills(lesson.conceptIds)}</div>${missing?`<aside class="notice"><strong>录音缺口</strong> · 开头${lesson.recording?.missingOpeningApprox?'约':''}${escape(Math.round(missing/60))}分钟未录到。下方保留文件内原时间戳，不把漏录部分补写为课堂事实。</aside>`:''}</header><div class="lesson-layout"><nav class="lesson-nav" aria-label="本课目录"><span class="nav-caption">IN THIS DOSSIER</span>${[...keys,'sources'].map((key,i)=>`<a href="#section-${key}" data-section="${key}"><span>${String(i+1).padStart(2,'0')}</span>${labels[key]}</a>`).join('')}</nav><div class="lesson-content">${keys.map((key,i)=>section(key,lesson,i)).join('')}<section class="detail-section" id="section-sources"><h2><span>07</span>原始资料</h2><p class="source-help">时间戳定位本页转录段落；PDF页码按物理页计。未提供可核实的录音定位链接。</p><ul class="source-list">${(lesson.sources||[]).map(s=>{const path=safePath(s.path);return `<li class="source-item"><div class="source-item-title"><span class="source-kind">${escape({transcript:'原始转录',courseware:'课件',analysis:'分析报告',personal:'个人记录'}[s.kind] || '资料')}</span>${path?`<a href="${path}" target="_blank" rel="noopener">${escape(s.label)} ↗</a>`:`<span>${escape(s.label)}</span>`}</div>${s.originalPath?`<div class="source-path">来源路径：${escape(s.originalPath)}</div>`:''}</li>`;}).join('')}</ul>${lesson.transcriptPath?`<details class="transcript-panel" id="transcript-panel" ${t?'open':''}><summary>逐段查阅原始转录</summary><p class="transcript-info">转录保留原有表达，可能包含误识别、口误和课间内容；不等同于校订讲义。</p><div class="transcript-tools"><label for="transcript-search">段落检索</label><input type="search" class="search-input" id="transcript-search" placeholder="在本次转录中查找"><span class="stat-caption" id="transcript-count"></span></div><div class="transcript-content" id="transcript-content" aria-live="polite"><p class="section-empty">正在读取原始转录……</p></div></details>`:'<p class="section-empty">当前未提供可读取的逐段转录文件。</p>'}</section></div></div><nav class="lesson-pager" aria-label="前后课堂">${index>0?`<a href="${lessonUrl(lessons[index-1].id)}"><small>← 前一份课堂档案</small>${escape(lessons[index-1].date)} · ${escape(lessons[index-1].title)}</a>`:''}${index<lessons.length-1?`<a href="${lessonUrl(lessons[index+1].id)}"><small>后一份课堂档案 →</small>${escape(lessons[index+1].date)} · ${escape(lessons[index+1].title)}</a>`:''}</nav>`;
    document.querySelectorAll('[data-section]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();document.querySelector('#section-'+a.dataset.section)?.scrollIntoView({behavior:'smooth'});}));
    renderMath();
    if(!lesson.transcriptPath)return;
    try {
      if(!transcriptCache.has(id)){const path=safePath(lesson.transcriptPath);if(!path)throw new Error('无效转录路径');const response=await fetch(path);if(!response.ok)throw new Error('转录文件无法读取');transcriptCache.set(id,await response.json());}
      if(currentGeneration!==generation)return;
      const data=transcriptCache.get(id);const blocks=Array.isArray(data)?data:(data.blocks || []);
      const showBlocks=q=>{const visible=blocks.filter(b=>[b.timestamp,b.text,b.speaker].join(' ').toLocaleLowerCase().includes(q.toLocaleLowerCase()));document.querySelector('#transcript-count').textContent=visible.length+' / '+blocks.length+' 段';document.querySelector('#transcript-content').innerHTML=visible.map(b=>`<article class="transcript-block ${t===b.timestamp?'is-selected':''}" id="transcript-${escape(b.id)}" ${t===b.timestamp?'tabindex="-1"':''}><div class="block-meta"><a href="${lessonUrl(id,b.timestamp)}">${escape(b.timestamp)}</a><span>${escape(b.speaker || '说话人未标注')}</span></div><p>${escape(b.text || '')}</p></article>`).join('') || '<p class="section-empty">没有匹配的转录段落。</p>';};
      showBlocks('');document.querySelector('#transcript-search').addEventListener('input',e=>showBlocks(e.target.value));
      if(t){const target=main.querySelector('.transcript-block.is-selected');document.querySelector('#transcript-panel').open=true;if(target){requestAnimationFrame(()=>{target.scrollIntoView({block:'center'});target.focus({preventScroll:true});});}else{const info=document.createElement('p');info.className='notice';info.textContent='没有找到这个精确时间戳。请按下方原文时间戳查阅，未自动匹配到其他段落。';document.querySelector('#transcript-content').before(info);document.querySelector('#transcript-panel').scrollIntoView();}}
    }catch(error){if(currentGeneration===generation){document.querySelector('#transcript-content').innerHTML='<p class="section-empty">原始转录暂时无法读取。请使用上方已核实的原文件链接查阅。</p>';console.error(error);}}
  }
  function renderMath(){if(typeof window.renderMathInElement==='function'){window.renderMathInElement(main,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false}],throwOnError:false,strict:'warn',trust:false});}else if(main.querySelector('.formula')){const note=document.createElement('p');note.className='math-unavailable';note.textContent='公式组件暂未加载，当前保留 LaTeX 原式。';main.prepend(note);}}
  function notFound(message){main.innerHTML=`<section class="error-state"><h1>这一份档案尚未入藏。</h1><p>${escape(message)}</p><a class="text-link" href="#/timeline">返回课堂时间线 ↗</a></section>`;}
  function route(){
    let raw=location.hash.slice(1) || '/';if(raw==='main')raw='/';const current=++generation;
    const [path,queryString='']=raw.split('?');const query=new URLSearchParams(queryString);const parts=path.split('/').filter(Boolean).map(s=>{try{return decodeURIComponent(s);}catch{return s;}});
    const name=parts[0] || 'home';document.querySelectorAll('[data-nav]').forEach(a=>{const active=a.dataset.nav===(name==='lesson'?'timeline':name==='concept'?'concepts':name);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    document.title='Probability Archive｜概率论课堂档案馆';
    if(name==='home')home();else if(name==='timeline')timeline();else if(name==='concepts')conceptIndex();else if(name==='concept')conceptDetail(parts[1]);else if(name==='lesson')lessonDetail(parts[1],query,current);else notFound('请从时间线或知识索引重新查找。');
    if(!query.has('t'))window.scrollTo(0,0);main.focus({preventScroll:true});
  }
  async function init(){try{const results=await Promise.all(['data/lessons.json','data/concepts.json'].map(async path=>{const r=await fetch(path);if(!r.ok)throw new Error('无法读取 '+path);return r.json();}));lessons=(results[0].lessons || []).slice().sort((a,b)=>a.date.localeCompare(b.date));course=results[0].course || {};concepts=results[1].concepts || [];window.addEventListener('hashchange',route);route();}catch(error){main.innerHTML=`<section class="error-state"><div class="eyebrow">Archive unavailable</div><h1>档案暂时无法翻开</h1><p>请通过本地 HTTP 服务器打开本项目，并确认 data 中的 JSON 文件已就绪。</p><p><code>python -m http.server 8000 --directory probability-atlas</code></p><p>${escape(error.message)}</p></section>`;console.error(error);}}
  document.addEventListener('click',event=>{
    if(event.button!==0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)return;
    const anchor=event.target.closest('a');if(!anchor)return;
    if(anchor.classList.contains('skip-link')){event.preventDefault();main.focus();return;}
    if(anchor.matches('a.timestamp, .block-meta a') && anchor.getAttribute('href')===location.hash){event.preventDefault();route();}
  });
  init();
})();
