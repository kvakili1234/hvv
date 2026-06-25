/* Heart Vein & Vascular — site interactions */
(function(){
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- mobile nav ---- */
  window.toggleMobNav = function(){ document.body.classList.toggle('mnav-open'); };
  window.closeMobNav  = function(){ document.body.classList.remove('mnav-open'); };
  document.addEventListener('click', function(e){
    var h = e.target.closest('.mn-head');
    if(h){ h.parentNode.classList.toggle('open'); }
  });

  /* ---- hero rotating text + images ---- */
  function initHero(){
    var slides = Array.prototype.slice.call(document.querySelectorAll('.hero .slide'));
    var imgs   = Array.prototype.slice.call(document.querySelectorAll('.hero-imgs img'));
    var dots   = Array.prototype.slice.call(document.querySelectorAll('.hero-dots button'));
    if(!slides.length) return;
    var i = 0, n = slides.length, timer;
    function go(k){
      i = (k + n) % n;
      slides.forEach(function(s,x){ s.classList.toggle('on', x===i); });
      if(imgs.length) imgs.forEach(function(s,x){ s.classList.toggle('on', x===(i % imgs.length)); });
      dots.forEach(function(d,x){ d.classList.toggle('on', x===i); });
    }
    function start(){ if(reduce) return; stop(); timer = setInterval(function(){ go(i+1); }, 5200); }
    function stop(){ if(timer) clearInterval(timer); }
    dots.forEach(function(d,x){ d.addEventListener('click', function(){ go(x); start(); }); });
    go(0); start();
    var hero = document.querySelector('.hero');
    if(hero){ hero.addEventListener('mouseenter', stop); hero.addEventListener('mouseleave', start); }
  }

  /* ---- reviews carousel ---- */
  function initReviews(){
    var track = document.getElementById('revTrack');
    if(!track) return;
    function page(dir){
      var card = track.querySelector('.rev-card');
      if(!card) return;
      var step = card.getBoundingClientRect().width + 22;
      var per = Math.max(1, Math.round(track.clientWidth / step));
      track.scrollBy({ left: dir * step * per, behavior: reduce ? 'auto' : 'smooth' });
    }
    var prev = document.getElementById('revPrev'), next = document.getElementById('revNext');
    if(prev) prev.addEventListener('click', function(){ page(-1); });
    if(next) next.addEventListener('click', function(){ page(1); });
    // loop next to start when at end
    if(next) next.addEventListener('click', function(){
      setTimeout(function(){
        if(track.scrollLeft + track.clientWidth >= track.scrollWidth - 4){
          setTimeout(function(){ track.scrollTo({left:0, behavior: reduce?'auto':'smooth'}); }, 1600);
        }
      }, 400);
    });
  }

  /* ---- appointment form (delivers via FormSubmit, no backend needed) ---- */
  window.submitForm = function(e){
    e.preventDefault();
    var form = e.target;
    var body = form.querySelector('.form-body');
    var ok   = form.parentNode.querySelector('.ok-msg');
    var btn  = form.querySelector('button[type=submit]');
    if(btn){ btn.disabled = true; btn.textContent = 'Sending…'; }
    var data = new FormData(form);
    fetch(form.action, { method:'POST', body:data, headers:{ 'Accept':'application/json' } })
      .then(function(r){ return r.json().catch(function(){ return {}; }); })
      .then(function(){ if(body) body.style.display='none'; if(ok) ok.style.display='block'; })
      .catch(function(){ if(body) body.style.display='none'; if(ok) ok.style.display='block'; });
    return false;
  };

  document.addEventListener('DOMContentLoaded', function(){ initHero(); initReviews(); });
})();
