const hero = document.getElementById('cycling_hero');
const main = document.getElementById('trips_overview');
const arrow = document.getElementById('cycling_hero_arrow');
let isScrolling = false;

// Helper function to detect mobile
function isMobile() {
  return window.innerWidth <= 800; // adjust breakpoint as needed
}


function updateNavbar() {
  const heroRect = hero.getBoundingClientRect();
  if (heroRect.bottom > 0) { // hero is still visible
    navbar.classList.add('hero_active');
    sidebar.classList.add('hero_active');
  } else {
    navbar.classList.remove('hero_active');
    sidebar.classList.remove('hero_active');
  }
}

updateNavbar();

// Smooth scroll from hero to main
function scrollToMain() {
  if (isScrolling) return;
  isScrolling = true;
  main.scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => {
    isScrolling = false;
    updateNavbar();
  }, 1000);
}

// Smooth scroll from main to hero
function scrollToHero() {
  if (isScrolling) return;
  isScrolling = true;
  hero.scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => {
    isScrolling = false;
    updateNavbar();
  }, 800);
}




// Arrow click scroll
arrow.addEventListener('click', scrollToMain);

if (!isMobile()) {
  // Detect wheel scroll on hero
  hero.addEventListener('wheel', e => {
    if (isScrolling) return;

    if (e.deltaY > 0) { // scroll down
      e.preventDefault(); // prevent default scroll
      scrollToMain();
    }
  }, { passive: false });



  let lastScrollY = 0; // track previous scroll position

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const scrollingUp = scrollY < lastScrollY;

    // Define threshold: only snap if within 50px of top of main
    let heroBottomY = hero.offsetTop + hero.offsetHeight;
    const threshold = heroBottomY;

    if (scrollingUp && scrollY < threshold && !isScrolling) {
      scrollToHero();
    }

    lastScrollY = scrollY;
  });



  window.addEventListener('wheel', e => {
    if (isScrolling) {
      e.preventDefault(); // block wheel events while animating
    }
  }, { passive: false });
}





window.addEventListener('scroll', updateNavbar);
