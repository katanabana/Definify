window.addEventListener('DOMContentLoaded', event => {

    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    let scrollToTopVisible = false;
    var m = true;
    // Closes the sidebar menu
    const menuToggle = document.body.querySelector('.menu-toggle');
    menuToggle.addEventListener('click', event => {
        event.preventDefault();
        sidebarWrapper.classList.toggle('active');
        menuToggle.classList.toggle('active');
        if (m) {
            document.getElementById("main").style.marginRight = "250px";
            m = false;
        }
        else {
            document.getElementById("main").style.marginRight = "0px";
            m = true;
        }
    })

    // Closes responsive menu when a scroll trigger link is clicked
    var scrollTriggerList = [].slice.call(document.querySelectorAll('#sidebar-wrapper .js-scroll-trigger'));
    scrollTriggerList.map(scrollTrigger => {
        scrollTrigger.addEventListener('click', () => {
            sidebarWrapper.classList.remove('active');
            menuToggle.classList.remove('active');
            document.getElementById("main").style.marginRight = "0px";
        })
    });



})

document.getElementById("pfp").onchange = function() {
    document.getElementById("enter-room-form").submit();
};