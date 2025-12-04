document.addEventListener('DOMContentLoaded', function() {
    // Highlight active navigation link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-nav a');

    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPath ||
            (linkHref.endsWith('/') && currentPath.startsWith(linkHref)) ||
            (linkHref === '/crypto/main_dashboard/' && (currentPath === '/' || currentPath === '/crypto/'))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Mobile menu toggle functionality
    const mobileMenuButton = document.getElementById('mobile-menu');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuButton && mainNav) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenuButton.classList.toggle('active');
            mainNav.classList.toggle('active');
            document.body.classList.toggle('no-scroll'); // Prevent scrolling when menu is open
        });

        // Close mobile menu when a link is clicked
        mainNav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenuButton.classList.remove('active');
                mainNav.classList.remove('active');
                document.body.classList.remove('no-scroll');
            });
        });
    }

    // Advanced Intersection Observer for scroll animations
    const animatedElements = document.querySelectorAll('[data-animate]');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const animationType = entry.target.dataset.animate;
                const animationDelay = entry.target.dataset.delay || '0s';
                entry.target.style.animationDelay = animationDelay;
                entry.target.classList.add('animated', animationType);
                observer.unobserve(entry.target); // Stop observing once animated
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }); // Trigger when 10% visible, shrink bottom margin

    animatedElements.forEach(element => {
        observer.observe(element);
    });

    // Add a simple fade-in for the main header once DOM is loaded
    const mainHeader = document.querySelector('.main-header');
    if (mainHeader) {
      mainHeader.style.opacity = '0';
      mainHeader.style.transition = 'opacity 0.5s ease-in';
      setTimeout(() => {
        mainHeader.style.opacity = '1';
      }, 100);
    }
});
