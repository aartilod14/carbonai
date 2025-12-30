// Theme toggle & persist
const themeBtn = document.querySelectorAll('#theme-toggle');
function setTheme(mode) {
  if (mode === 'dark') document.body.classList.add('dark');
  else document.body.classList.remove('dark');
  localStorage.setItem('eco_theme', mode);
}
document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('eco_theme') || 'light';
  setTheme(savedTheme);

  // multiple theme buttons across pages
  document.querySelectorAll('#theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const now = document.body.classList.contains('dark') ? 'light' : 'dark';
      setTheme(now);
      btn.textContent = now === 'dark' ? 'Light' : 'Dark';
    });
    // set initial text
    btn.textContent = document.body.classList.contains('dark') ? 'Light' : 'Dark';
  });

  // Auto-fill form from localStorage on index
  const travel = document.getElementById('travel');
  if (travel) {
    const saved = JSON.parse(localStorage.getItem('eco_inputs') || '{}');
    if (saved.travel) travel.value = saved.travel;
    const electricity = document.getElementById('electricity');
    const diet = document.getElementById('diet');
    const shopping = document.getElementById('shopping');
    if (saved.electricity) electricity.value = saved.electricity;
    if (saved.diet) diet.value = saved.diet;
    if (saved.shopping) shopping.value = saved.shopping;

    // Save on change
    [travel, electricity, diet, shopping].forEach(el => {
      el.addEventListener('input', () => {
        const payload = {
          travel: travel.value,
          electricity: electricity.value,
          diet: diet.value,
          shopping: shopping.value
        };
        localStorage.setItem('eco_inputs', JSON.stringify(payload));
      });
    });

    // Reset button
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        travel.value = electricity.value = diet.value = shopping.value = '';
        localStorage.removeItem('eco_inputs');
      });
    }
  }
});
function triggerConfetti(points){
    for(let i=0;i<50;i++){
        let el = document.createElement('div');
        el.className='confetti';
        el.style.position='absolute';
        el.style.left=Math.random()*window.innerWidth+'px';
        el.style.top='0px';
        el.style.width='5px';
        el.style.height='10px';
        el.style.background=['#00ff00','#00cc00','#009900'][Math.floor(Math.random()*3)];
        el.style.opacity=0.8;
        el.style.transition='all 2s linear';
        document.body.appendChild(el);
        setTimeout(()=>{
            el.style.top='100vh';
        },50);
        setTimeout(()=>el.remove(),2100);
    }
}
