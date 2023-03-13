/** start event for menu button */

let menuButton = document.querySelector('.menuButton');
let menu = document.querySelector('.menu');

if(menuButton != null) {
    menuButton.addEventListener('click',function () {
        menu.classList.toggle('showMenu');
    });
}

window.onresize = () => {
    if(menu.classList.contains('showMenu') && window.innerWidth > 1056)
    menu.classList.remove('showMenu');
}