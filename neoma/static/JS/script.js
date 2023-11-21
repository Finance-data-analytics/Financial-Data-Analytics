window.addEventListener('DOMContentLoaded', (event) => {
  const element = document.querySelector('.element');
  element.classList.add('active');
});

window.addEventListener('scroll', () => {
  const elementPosition = element.getBoundingClientRect().top;
  const viewPortHeight = window.innerHeight;

  if(scrollTop > (scrollTop + topElementToTopViewport).toFixed() - clientHeight * 0.5){
      element.classList.add('active');
  }
  //if(elementPosition < viewPortHeight) {
  //}
});
// This function will add a class to elements with the 'animate-on-scroll' class when they enter the viewport
function onScroll() {
  console.log('Scrolled!');
  const windowHeight = window.innerHeight;
  const elements = document.querySelectorAll('.animate-on-scroll');

  elements.forEach((element) => {
    const positionFromTop = element.getBoundingClientRect().top;
    console.log(positionFromTop, windowHeight);

    if (positionFromTop - windowHeight <= 0) {
      element.classList.add('active'); // 'active' is the class that contains your animation or transition
    }
  });
}

window.addEventListener('scroll', onScroll);

// Run onScroll at least once to check if any animatable elements are already in view on page load
onScroll();

window.addEventListener('scroll', function() {
  var element = document.querySelector('.your-element-class');
  var position = element.getBoundingClientRect();

  // vérifiant si l'élément est dans le viewport
  if(position.top < window.innerHeight && position.bottom >= 0) {
    element.classList.add('slide-in'); // ajoute la classe d'animation
  }
});

const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');


registerBtn.addEventListener('click', () => {
  container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
  container.classList.remove("active");
});

document.addEventListener("DOMContentLoaded", function() {
var currentSlide = 0;
var slides = document.querySelectorAll(".slide");
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');

function showSlide(index) {
    // Masquer toutes les slides
    slides.forEach(slide => {
        slide.style.display = 'none';
    });

    // Afficher la slide demandée
    slides[index].style.display = 'block';
}

nextBtn.addEventListener('click', () => {
    if (currentSlide < slides.length - 1) {
        currentSlide++;
        showSlide(currentSlide);
    }
});

prevBtn.addEventListener('click', () => {
    if (currentSlide > 0) {
        currentSlide--;
        showSlide(currentSlide);
    }
});

// Initialisation
showSlide(currentSlide);
});
function navigate(step) {
  var index = 0;
  var sections = document.querySelectorAll('.form-section');
  var currentSection = document.querySelector('.form-section:not([style*="display: none"])');
  
  // Trouver l'index de la section actuelle
  sections.forEach((section, i) => {
      if (section === currentSection) {
          index = i;
      }
  });

  // Calculer l'index de la nouvelle section
  var newIndex = index + step;

  // Si la nouvelle section est dans la plage valide
  if (newIndex >= 0 && newIndex < sections.length) {
      currentSection.style.display = 'none'; // Masquer la section actuelle
      sections[newIndex].style.display = 'block'; // Afficher la nouvelle section
  }
  container.classList.toggle('active', step > 0);
}
function renamePortfolio(portfolioId) {
  // Affichez le formulaire de renommage
  document.getElementById('renameForm').style.display = 'block';
  
  // Stockez l'ID du portfolio dans un élément du formulaire pour une utilisation ultérieure
  document.getElementById('renameForm').dataset.portfolioId = portfolioId;
}

function submitRename() {
  var portfolioId = document.getElementById('renameForm').dataset.portfolioId;
  var newName = document.getElementById('newName').value;

  // Utilisez AJAX pour envoyer la demande de renommage
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/rename_portfolio', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
      portfolioId: portfolioId,
      newName: newName
  }));

  xhr.onload = function () {
      if (xhr.status == 200) {
          // Mise à jour réussie, cachez le formulaire et actualisez la page ou mettez à jour l'interface utilisateur
          document.getElementById('renameForm').style.display = 'none';
          location.reload(); // Ou mettez à jour l'interface utilisateur comme nécessaire
      } else {
          // Gérer les erreurs ici
          alert('Error renaming portfolio.');
      }
  };
}

function updateProgressBar() {
    fetch('/loading_status')
    .then(response => response.json())
    .then(data => {
        let progress = data.progress;
        document.getElementById('progress-bar').style.width = progress + '%';
    });
}

setInterval(updateProgressBar, 1000);  // Mettre à jour la barre toutes les secondes
