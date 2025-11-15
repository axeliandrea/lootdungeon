// Lucky Wheel Game Logic
class LuckyWheel {
    constructor() {
        this.isSpinning = false;
        this.rewards = [
            '50 Gold',
            'Rare Sword', 
            '100 Gold',
            'Epic Shield',
            '75 Gold',
            'Legendary Potion',
            '25 Gold',
            'Mystic Ring'
        ];
        
        this.init();
    }
    
    init() {
        this.wheel = document.getElementById('wheel');
        this.spinBtn = document.getElementById('spinBtn');
        this.result = document.getElementById('result');
        
        // Add event listeners
        this.spinBtn.addEventListener('click', () => this.spinWheel());
        
        console.log('🎰 Lucky Wheel initialized!');
    }
    
    spinWheel() {
        if (this.isSpinning) return;
        
        this.isSpinning = true;
        this.result.textContent = '';
        
        // Disable button and show spinning state
        this.spinBtn.disabled = true;
        this.spinBtn.textContent = 'SPINNING...';
        this.spinBtn.style.opacity = '0.7';
        
        // Random rotation between 1800-3600 degrees (5-10 full rotations)
        const randomRotation = Math.random() * 1800 + 1800;
        const finalRotation = randomRotation % 360;
        
        // Apply rotation with smooth animation
        this.wheel.style.transform = `rotate(${randomRotation}deg)`;
        this.wheel.classList.add('spinning');
        
        // Play spin sound effect (optional)
        this.playSpinSound();
        
        // Determine result after animation completes
        setTimeout(() => {
            this.determineWinner(finalRotation);
        }, 3000);
    }
    
    determineWinner(finalRotation) {
        // Calculate which segment the pointer landed on
        // Each segment is 45 degrees (360/8)
        const segmentIndex = Math.floor((360 - finalRotation) / 45) % 8;
        const reward = this.rewards[segmentIndex];
        
        // Show result
        this.result.innerHTML = `🎉 <strong>${reward}!</strong>`;
        this.result.classList.add('winning');
        
        // Add glow effect to wheel
        this.wheel.classList.add('glow');
        
        // Reset button after animation
        setTimeout(() => {
            this.resetSpin();
        }, 1000);
    }
    
    resetSpin() {
        this.result.classList.remove('winning');
        this.wheel.classList.remove('glow', 'spinning');
        
        this.spinBtn.disabled = false;
        this.spinBtn.textContent = 'SPIN AGAIN';
        this.spinBtn.style.opacity = '1';
        
        this.isSpinning = false;
    }
    
    playSpinSound() {
        // Simple Web Audio API sound effect
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.5);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Audio not supported or blocked');
        }
    }
}

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LuckyWheel();
});

// Global function for button onclick (backup)
function spinWheel() {
    // This function is kept for backward compatibility
    // The main logic is handled by the LuckyWheel class
    console.log('🔄 Spin triggered via global function');
}
