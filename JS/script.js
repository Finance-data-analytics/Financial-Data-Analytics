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