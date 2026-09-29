'use strict';
const en = document.body.dataset.lang === 'en';
const colors = {M2:'#247978', M3:'#d37646', M4:'#8174ad'};
const labels = {M2:'ViPE + DA3', M3:'ORB-SLAM3 + DA3', M4:'GT pose + DA3'};
let split = 'eval_500';
const progress = document.querySelector('.progress');
function updateProgress() {
  const length = document.documentElement.scrollHeight - innerHeight;
  progress.style.width = `${length > 0 ? Math.min(100, scrollY / length * 100) : 0}%`;
}
addEventListener('scroll', updateProgress, {passive:true});
addEventListener('resize', updateProgress);
updateProgress();
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) if (entry.isIntersecting) {
    document.querySelectorAll('.toc a').forEach(a => a.classList.toggle('active', a.hash === `#${entry.target.id}`));
  }
}, {rootMargin:'-10% 0px -70% 0px'});
document.querySelectorAll('h2[id]').forEach(h => observer.observe(h));

async function getJSON(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}: ${response.status}`);
  return response.json();
}
getJSON('data/summary.json').then(data => {
  const metricControl = document.getElementById('depth-metric');
  function renderBars() {
    const metric = metricControl.value;
    const isPercent = ['absrel','valid_coverage','delta1'].includes(metric);
    const values = Object.keys(colors).map(m => data.depth[split].methods[m].primary_no_scale_fit[metric]);
    const max = ['valid_coverage','delta1'].includes(metric) ? 1 : Math.max(...values) * 1.12;
    document.getElementById('depth-bars').innerHTML = Object.keys(colors).map((method,index) => {
      const value = values[index];
      const display = isPercent ? `${(value*100).toFixed(2)}%` : `${value.toFixed(4)}`;
      return `<div class="bar-row"><div class="bar-label">${method}<small>${labels[method]}</small></div><div class="bar-track"><div class="bar-fill" style="--bar:${colors[method]};width:${value/max*100}%"></div></div><div class="bar-value">${display}</div></div>`;
    }).join('') + `<p class="axis-note">${en?'Shared axis from zero':'共用从零开始的坐标轴'} · ${metricControl.selectedOptions[0].textContent}</p>`;
    document.getElementById('depth-chart-note').textContent = en ? `${data.depth[split].frame_count} frames · pooled pixels · no GT scale fitting. Coverage and penalized MAE retain missing predictions.` : `${data.depth[split].frame_count} 帧 · 按像素聚合 · 不拟合 GT 尺度。覆盖率与缺失惩罚 MAE 保留缺失预测的影响。`;
  }
  document.querySelectorAll('[data-split]').forEach(button => button.addEventListener('click', () => {
    split = button.dataset.split;
    document.querySelectorAll('[data-split]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    renderBars();
  }));
  metricControl.addEventListener('change',renderBars);
  renderBars();
}).catch(() => {
  document.getElementById('depth-bars').textContent = en ? 'Interactive data could not load. Complete results are in the tables below.' : '交互数据加载失败，请查看下方完整表格。';
});

getJSON('data/trajectories.json').then(data => {
  const svg = document.getElementById('trajectory-svg');
  const control = document.getElementById('projection');
  const series = [['gt_position','#253a45','GT'],['orb_slam3_position','#d37646','ORB-SLAM3'],['vipe_default_position','#247978','ViPE'],['openvins_position','#8174ad','OpenVINS']];
  function renderTrajectory() {
    const [a,b] = control.value.split(',').map(Number);
    const all = series.flatMap(([key])=>data[key]);
    const xmin = Math.min(...all.map(p=>p[a])), xmax = Math.max(...all.map(p=>p[a]));
    const ymin = Math.min(...all.map(p=>p[b])), ymax = Math.max(...all.map(p=>p[b]));
    const scale = Math.min(630/Math.max(xmax-xmin,.1),265/Math.max(ymax-ymin,.1));
    const cx=(xmax+xmin)/2, cy=(ymax+ymin)/2;
    const x=v=>390+(v-cx)*scale, y=v=>167-(v-cy)*scale;
    let markup = '';
    for (let i=0;i<=4;i++) {
      const vx=xmin+(xmax-xmin)*i/4, vy=ymin+(ymax-ymin)*i/4;
      markup+=`<line x1="${x(vx)}" x2="${x(vx)}" y1="22" y2="308" stroke="#e4e9e3"/><text x="${x(vx)}" y="328" text-anchor="middle" font-size="11" fill="#667679">${vx.toFixed(1)}</text>`;
      markup+=`<line x1="65" x2="717" y1="${y(vy)}" y2="${y(vy)}" stroke="#e4e9e3"/><text x="52" y="${y(vy)+4}" text-anchor="end" font-size="11" fill="#667679">${vy.toFixed(1)}</text>`;
    }
    for (const [key,color,label] of series) {
      const points = data[key].map(p=>`${x(p[a]).toFixed(2)},${y(p[b]).toFixed(2)}`).join(' ');
      markup+=`<polyline points="${points}" fill="none" stroke="${color}" stroke-width="${key==='gt_position'?2.5:1.6}" opacity=".9"><title>${label}</title></polyline>`;
    }
    markup+=`<text x="390" y="353" text-anchor="middle" font-size="11" fill="#667679">${['X','Y','Z'][a]} (m)</text><text x="10" y="18" font-size="11" fill="#667679">${['X','Y','Z'][b]} (m)</text>`;
    svg.innerHTML=markup;
  }
  control.addEventListener('change',renderTrajectory);
  renderTrajectory();
}).catch(() => {
  document.getElementById('trajectory-svg').outerHTML = `<p>${en?'Interactive data could not load. See the static figure above.':'交互数据加载失败，请查看上方静态图。'}</p>`;
});
