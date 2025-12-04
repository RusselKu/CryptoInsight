document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('backgroundCanvas');
    if (!canvas) return; // Exit if canvas element is not found

    const ctx = canvas.getContext('2d');
    let particles = [];
    const numParticles = 70; // Reduced for performance, adjust as needed
    const maxParticleSpeed = 0.6; // Max speed for particles
    const lineDistance = 120; // Max distance for lines between particles
    const cryptoShapes = ['₿', 'Ξ', '⟠', '◇', '☍']; // Bitcoin, Ethereum, generic symbols

    // Resize canvas to fill window
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = document.documentElement.scrollHeight; // Cover full scrollable height
        // Recalculate particle positions if needed, or simply re-initialize
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas(); // Initial resize

    // Particle constructor
    function Particle(x, y) {
        this.x = x || Math.random() * canvas.width;
        this.y = y || Math.random() * canvas.height;
        this.speedX = (Math.random() - 0.5) * maxParticleSpeed * 2;
        this.speedY = (Math.random() - 0.5) * maxParticleSpeed * 2;
        this.size = Math.random() * 2 + 1; // 1 to 3
        this.color = `rgba(0, 173, 181, ${Math.random() * 0.5 + 0.3})`; // Teal with varying opacity
        this.shape = cryptoShapes[Math.floor(Math.random() * cryptoShapes.length)];
        this.fontSize = Math.random() * 15 + 10; // 10 to 25
    }

    Particle.prototype.update = function() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Bounce off edges
        if (this.x > canvas.width || this.x < 0) this.speedX *= -1;
        if (this.y > canvas.height || this.y < 0) this.speedY *= -1;

        // Draw particle as a shape
        ctx.fillStyle = this.color;
        ctx.font = `${this.fontSize}px Arial`; // Use a simple font for symbols
        ctx.fillText(this.shape, this.x, this.y);
    };

    // Initialize particles
    function init() {
        particles = [];
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle());
        }
    }

    // Connect particles with lines
    function connect() {
        for (let a = 0; a < particles.length; a++) {
            for (let b = a; b < particles.length; b++) {
                let distance = Math.sqrt(
                    (particles[a].x - particles[b].x) ** 2 +
                    (particles[a].y - particles[b].y) ** 2
                );
                if (distance < lineDistance) {
                    ctx.strokeStyle = `rgba(0, 173, 181, ${1 - (distance / lineDistance)})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(particles[a].x, particles[a].y);
                    ctx.lineTo(particles[b].x, particles[b].y);
                    ctx.stroke();
                }
            }
        }
    }

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
        }
        connect();
    }

    init();
    animate();
});
