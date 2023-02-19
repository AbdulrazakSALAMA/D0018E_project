/** start event for menu button */

let menuButton = document.querySelector('.menuButton');
let menu = document.querySelector('.menu');
menuButton.addEventListener('click',function () {
    menu.classList.toggle('showMenu');
});