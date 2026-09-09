/* =========================================================
   FAHIM — portfolio
   1) Liste des productions à afficher dans le bandeau défilant
   2) Reveal au scroll (une seule fois, léger, perf-safe)
   ========================================================= */

/* --------------------------------------------------------
   1) PRODUCTIONS
   -----------------------------------------------------------
   Remplace les entrées ci-dessous par tes vraies vidéos.
   - id     : l'identifiant YouTube (dans l'URL, après "v=")
   - title  : le nom du client / projet affiché sous la vignette
   La vignette est générée automatiquement depuis YouTube,
   donc tu n'as besoin de fournir que l'id et le titre.

   ⚠️ Le lien de playlist que tu as donné semble incomplet
   (l'identifiant "PLefpG9mfor5Q" n'est pas une playlist
   publique valide de mon côté), donc j'ai mis des exemples
   en attendant — remplace-les par tes vraies vidéos ou
   donne-moi la liste des ids et je les intègre directement.
-------------------------------------------------------- */
const PRODUCTIONS = [
  { id: "dQw4w9WgXcQ", title: "Client / Projet — à remplacer" },
  { id: "05v9iZDl5PU", title: "Client / Projet — à remplacer" },
  { id: "jNQXAC9IVRw", title: "Client / Projet — à remplacer" },
  { id: "9bZkp7q19f0", title: "Client / Projet — à remplacer" },
  { id: "3JZ_D3ELwOQ", title: "Client / Projet — à remplacer" },
  { id: "L_jWHffIx5E", title: "Client / Projet — à remplacer" },
];

function renderMarquee(){
  const track = document.getElementById("marqueeTrack");
  if (!track || PRODUCTIONS.length === 0) return;

  const cardHTML = (p) => `
    <a class="prod-card" href="https://www.youtube.com/watch?v=${p.id}" target="_blank" rel="noopener">
      <img src="https://i.ytimg.com/vi/${p.id}/hqdefault.jpg" alt="${p.title}" loading="lazy" width="200" height="112">
      <p class="prod-card__title">${p.title}</p>
    </a>`;

  // dupliqué une fois pour permettre une boucle de scroll parfaitement continue
  track.innerHTML = PRODUCTIONS.map(cardHTML).join("") + PRODUCTIONS.map(cardHTML).join("");
}

/* --------------------------------------------------------
   2) REVEAL AU SCROLL
-------------------------------------------------------- */
function initReveal(){
  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window) || items.length === 0){
    items.forEach(el => el.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting){
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: "0px 0px -60px 0px" });

  items.forEach(el => observer.observe(el));
}

document.addEventListener("DOMContentLoaded", () => {
  renderMarquee();
  initReveal();
});
