'use strict';
(()=>{
 let filter='all';const query=document.querySelector('#search');const cards=[...document.querySelectorAll('#facts article')];
 function apply(){let n=0;for(const card of cards){const type=filter==='all'||(filter==='unfinished'?card.dataset.status!=='done':card.dataset.subject===filter);card.hidden=!(type&&card.textContent.toLowerCase().includes(query.value.trim().toLowerCase()));if(!card.hidden)n++;}document.querySelector('#count').textContent='当前显示 '+n+' 条事实';}
 document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));apply();}));
 query.addEventListener('input',apply);
 function reveal(hash){let id;try{id=decodeURIComponent(hash.slice(1));}catch{return;}const target=document.getElementById(id);if(target?.matches('#facts article')){filter='all';query.value='';document.querySelector('[data-filter=all]').click();target.scrollIntoView();}}
 document.addEventListener('click',event=>{const link=event.target.closest('a[href^="#"]');if(link)reveal(link.getAttribute('href'));});
 addEventListener('hashchange',()=>reveal(location.hash));apply();reveal(location.hash);
})();
