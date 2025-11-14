// Lucky Wheel Game Logic
class LuckyWheel {
    constructor() {
        this.wheel = document.getElementById('wheel');
        this.spinButton = document.getElementById('spinButton');
        this.resultDisplay = document.getElementById('resultDisplay');
        this.rewardText = document.getElementById('rewardText');
        this.spinsLeftElement = document.getElementById('spinsLeft');
        this.totalGoldElement = document.getElementById('totalGold');
        this.totalItemsElement = document.getElementById('totalItems');
        this.confettiContainer = document.getElementById('confetti');
        
        this.maxSpins = 5;
        this.currentSpins = this.maxSpins;
        this.isSpinning = false;
        
        // Rewards configuration
        this.rewards = [
            { type: 'gold', amount: 50, label: '50 Gold', item: null },
            { type: 'item', name: 'Rare Sword', item: 'sword' },
            { type: 'gold', amount: 100, label: '100 Gold', item: null },
            { type: 'item', name: 'Epic Shield', item: 'shield' },
            { type: 'gold', amount: 75, label: '75 Gold', item: null },
            { type: 'item', name: 'Legendary Potion', item: 'potion' },
            { type: 'gold', amount: 25, label: '25 Gold', item: null },
            { type: 'item', name: 'Mystic Ring', item: 'ring' }
        ];
        
        // Player stats
        this.totalGold = 0;
        this.collectedItems = new Set();
        this.inventory = [];
        
        this.init();
    }
    
    init() {
        this.loadGameData();
        this.updateUI();
        this.attachEventListeners();
        
        // Check if this is the first visit
        if (!localStorage.getItem('lootdungeon_visited')) {
            this.showWelcomeMessage();
            localStorage.setItem('lootdungeon_visited', 'true');
        }
    }
    
    attachEventListeners() {
        this.spinButton.addEventListener('click', () => this.spin());
        
        // Add keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isSpinning) {
                e.preventDefault();
                this.spin();
            }
        });
    }
    
    showWelcomeMessage() {
        this.rewardText.textContent = 'Selamat datang di LootDungeon! Tekan PUTAR untuk memulai petualangan Anda!';
        this.resultDisplay.style.animation = 'slideInUp 0.6s ease-out';
    }
    
    spin() {
        if (this.isSpinning || this.currentSpins <= 0) {
            return;
        }
        
        this.isSpinning = true;
        this.spinButton.disabled = true;
        this.spinButton.textContent = 'BERPUTAR...';
        
        // Calculate random rotation
        const randomRotation = Math.random() * 360 + 1800; // 5 full rotations + random
        const segmentAngle = 360 / this.rewards.length;
        const winningSegmentIndex = Math.floor((randomRotation % 360) / segmentAngle);
        
        // Apply rotation
        this.wheel.style.transform = `rotate(${randomRotation}deg)`;
        
        // Add spinning class
        this.wheel.classList.add('spinning');
        
        // Calculate result after animation
        setTimeout(() => {
            this.processResult(winningSegmentIndex);
            this.isSpinning = false;
            this.wheel.classList.remove('spinning');
            this.spinButton.disabled = false;
            this.spinButton.innerHTML = '<span>PUTAR</span>';
        }, 3000);
    }
    
    processResult(segmentIndex) {
        const reward = this.rewards[segmentIndex];
        const result = this.calculateReward(reward);
        
        // Update displays
        this.rewardText.textContent = `🎉 ${result.message}`;
        this.resultDisplay.style.animation = 'slideInUp 0.6s ease-out';
        
        // Update stats
        this.updateStats(result);
        
        // Reduce spins
        this.currentSpins--;
        this.spinsLeftElement.textContent = this.currentSpins;
        
        // Show confetti for special rewards
        if (reward.type === 'item' || result.isJackpot) {
            this.showConfetti();
            this.playSound('success');
        }
        
        // Check if game over
        if (this.currentSpins <= 0) {
            this.endGame();
        }
        
        // Save game data
        this.saveGameData();
    }
    
    calculateReward(reward) {
        let result = {
            message: '',
            gold: 0,
            item: null,
            isJackpot: false
        };
        
        if (reward.type === 'gold') {
            result.gold = reward.amount;
            result.message = `${reward.label} ditambahkan ke gold Anda!`;
            
            // Jackpot chance (10%)
            if (Math.random() < 0.1) {
                result.gold *= 2;
                result.isJackpot = true;
                result.message = `🎰 JACKPOT! ${result.gold} Gold ditambahkan!`;
            }
        } else if (reward.type === 'item') {
            result.item = reward.item;
            result.message = `🗡️ ${reward.name} berhasil didapat!`;
            
            // Check if first time getting this item
            if (!this.collectedItems.has(reward.item)) {
                this.collectedItems.add(reward.item);
                result.message += ' (Item baru!)';
            }
            
            // Rare item chance (5%)
            if (Math.random() < 0.05 && !reward.name.includes('Legendary')) {
                result.message += ' 🌟 Item langka!';
            }
        }
        
        return result;
    }
    
    updateStats(result) {
        // Update gold
        this.totalGold += result.gold;
        this.totalGoldElement.textContent = this.totalGold;
        
        // Update items
        if (result.item) {
            this.inventory.push({
                name: this.rewards.find(r => r.item === result.item)?.name || result.item,
                type: result.item,
                timestamp: Date.now()
            });
            this.totalItemsElement.textContent = this.collectedItems.size;
        }
        
        // Animate stat changes
        this.animateNumber(this.totalGoldElement, this.totalGold - result.gold, this.totalGold);
        this.animateNumber(this.totalItemsElement, this.collectedItems.size - (result.item ? 1 : 0), this.collectedItems.size);
    }
    
    animateNumber(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (end - start) * easeOut);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }
    
    showConfetti() {
        const colors = ['#ffd700', '#ff6b6b', '#4ade80', '#a78bfa', '#fbbf24'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti-piece';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDelay = Math.random() * 3 + 's';
                confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                
                this.confettiContainer.appendChild(confetti);
                
                // Remove confetti after animation
                setTimeout(() => {
                    if (confetti.parentNode) {
                        confetti.parentNode.removeChild(confetti);
                    }
                }, 5000);
            }, i * 50);
        }
    }
    
    playSound(type) {
        // Create audio feedback
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            if (type === 'success') {
                oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
                oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
                oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            } else {
                oscillator.frequency.setValueAtTime(220, audioContext.currentTime); // A3
            }
            
            oscillator.type = 'sine';
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            // Fallback if audio context is not supported
            console.log('Audio feedback not supported');
        }
    }
    
    endGame() {
        this.spinButton.disabled = true;
        this.spinButton.textContent = 'HABIS';
        
        // Show final stats
        setTimeout(() => {
            this.showFinalStats();
        }, 2000);
    }
    
    showFinalStats() {
        const goldEarned = this.totalGold;
        const itemsFound = this.collectedItems.size;
        
        this.rewardText.innerHTML = `
            🎮 <strong>Permainan Selesai!</strong><br>
            💰 Total Gold: ${goldEarned}<br>
            🎒 Items: ${itemsFound}<br>
            <small>Segarkan halaman untuk main lagi!</small>
        `;
        
        // Show special celebration if player did well
        if (goldEarned > 200 || itemsFound >= 3) {
            this.showConfetti();
            this.rewardText.innerHTML += '<br>🏆 Anda adalah pemain yang luar biasa!';
        }
    }
    
    loadGameData() {
        const savedData = localStorage.getItem('lootdungeon_game');
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                this.currentSpins = data.currentSpins || this.maxSpins;
                this.totalGold = data.totalGold || 0;
                this.collectedItems = new Set(data.collectedItems || []);
                this.inventory = data.inventory || [];
            } catch (e) {
                console.log('Error loading saved data:', e);
            }
        }
    }
    
    saveGameData() {
        const gameData = {
            currentSpins: this.currentSpins,
            totalGold: this.totalGold,
            collectedItems: Array.from(this.collectedItems),
            inventory: this.inventory,
            lastPlay: Date.now()
        };
        
        localStorage.setItem('lootdungeon_game', JSON.stringify(gameData));
    }
    
    updateUI() {
        this.spinsLeftElement.textContent = this.currentSpins;
        this.totalGoldElement.textContent = this.totalGold;
        this.totalItemsElement.textContent = this.collectedItems.size;
    }
    
    // Reset game functionality
    reset() {
        localStorage.removeItem('lootdungeon_game');
        this.currentSpins = this.maxSpins;
        this.totalGold = 0;
        this.collectedItems.clear();
        this.inventory = [];
        this.updateUI();
        this.rewardText.textContent = 'Game telah direset. Selamat bermain!';
        this.spinButton.disabled = false;
        this.spinButton.innerHTML = '<span>PUTAR</span>';
    }
}

// Easter egg: Konami code
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // Up Up Down Down Left Right Left Right B A

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.toString() === konamiSequence.toString()) {
        // Easter egg activated
        const luckyWheel = window.luckyWheel;
        if (luckyWheel) {
            luckyWheel.maxSpins = 10;
            luckyWheel.currentSpins = 10;
            luckyWheel.updateUI();
            
            // Show message
            luckyWheel.rewardText.innerHTML = '🎮 <strong>Cheat Activated!</strong><br>Kesempatan ditambahkan menjadi 10!';
            
            // Reset konami code
            konamiCode = [];
            
            // Special confetti
            luckyWheel.showConfetti();
        }
    }
});

// Initialize the game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.luckyWheel = new LuckyWheel();
});

// Add some additional visual effects
document.addEventListener('mousemove', (e) => {
    const cursor = document.querySelector('.cursor-glow');
    if (!cursor) {
        const glow = document.createElement('div');
        glow.className = 'cursor-glow';
        glow.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            transition: transform 0.1s ease;
        `;
        document.body.appendChild(glow);
    }
    
    const glow = document.querySelector('.cursor-glow');
    glow.style.left = e.clientX - 10 + 'px';
    glow.style.top = e.clientY - 10 + 'px';
});

// Add performance optimization for mobile
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {
            // Service worker registration failed - this is okay for a demo
        });
    });
}
