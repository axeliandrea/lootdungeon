# LootDungeon - Lucky Wheel Game

🎰 **Lucky Wheel Game yang Interaktif untuk Web**

Lucky wheel yang menarik dengan efek visual, animasi, dan sistem reward yang seru untuk diploy di GitHub Pages.

## ✨ Fitur

### 🎮 Gameplay
- **8 Segmen Berbeda**: Setiap segmen memiliki reward unik
- **Sistem Kesempatan**: 5 kesempatan per game
- **Reward Variety**: Gold dan Items (Sword, Shield, Potion, Ring)
- **Jackpot System**: 10% chance untuk double gold
- **Item Collection**: Koleksi item langka dengan tracking

### 🎨 Visual & Effects
- **Animasi Smooth**: Transisi wheel yang halus dan realistis
- **Confetti Celebration**: Efek confetti untuk reward special
- **Responsive Design**: Optimal di desktop, tablet, dan mobile
- **Gradient Styling**: Desain modern dengan gradien warna
- **Cursor Effects**: Efek glow cursor yang interaktif

### 🔧 Technical Features
- **Local Storage**: Simpan progress game
- **Keyboard Support**: Tekan SPASI untuk spin
- **Audio Feedback**: Sound effects untuk aksi
- **Easter Egg**: Konami Code untuk bonus spins
- **Performance Optimized**: Efficient rendering untuk mobile

## 📁 Struktur File

```
/
├── index.html          # Main HTML structure
├── styles.css          # Complete styling & animations
├── script.js           # Game logic & interactivity
└── README.md          # This documentation
```

## 🚀 Deploy ke GitHub Pages

### Langkah 1: Buat Repository Baru
1. Buat repository baru di GitHub dengan nama `lootdungeon`
2. Set repository sebagai Public

### Langkah 2: Upload Files
1. Download semua file dari workspace ini
2. Upload file `index.html`, `styles.css`, dan `script.js` ke repository
3. Commit dan push changes

### Langkah 3: Enable GitHub Pages
1. Buka repository settings
2. Scroll ke bagian "Pages"
3. Pilih Source: "Deploy from a branch"
4. Pilih Branch: "main"
5. Pilih Folder: "/ (root)"
6. Klik Save

### Langkah 4: Custom Domain (Opsional)
1. Di settings Pages, masukkan custom domain `lootdungeon.online`
2. Konfigurasi DNS sesuai instruksi GitHub

## 🎯 Cara Bermain

### Dasar
1. **Klik PUTAR** atau tekan **SPASI** untuk memulai
2. **Wheel berputar** dengan animasi smooth
3. **Lihat hasil** di bagian result display
4. **Kumpulkan reward** dan lihat stats di bawah

### Reward System
- **Gold (25-100)**: Ditambahkan ke total gold
- **Items**: Rare Sword, Epic Shield, Legendary Potion, Mystic Ring
- **Jackpot**: 10% chance untuk double gold
- **Special Items**: 5% chance untuk item langka

### Stats Tracking
- **Total Gold**: Akumulasi semua gold yang didapat
- **Items Collected**: Jumlah item unik yang dikoleksi
- **Progress**: Tetap tersimpan menggunakan localStorage

## 🎮 Easter Eggs

### Konami Code
Tekan sequence berikut untuk bonus spins:
`↑ ↑ ↓ ↓ ← → ← → B A`

### Keyboard Shortcuts
- **SPASI**: Spin the wheel
- **Mouse Hover**: Efek cursor yang interaktif

## 🛠️ Kustomisasi

### Mengubah Reward
Edit array `rewards` di `script.js`:
```javascript
this.rewards = [
    { type: 'gold', amount: 50, label: '50 Gold', item: null },
    { type: 'item', name: 'New Item', item: 'newitem' },
    // Tambah reward lainnya
];
```

### Mengubah Kesempatan
Edit property `maxSpins` di `script.js`:
```javascript
this.maxSpins = 5; // Ubah sesuai diinginkan
```

### Mengubah Warna Segmen
Edit CSS segments di `styles.css`:
```css
.segment-1 {
    background: linear-gradient(45deg, #your-color-1, #your-color-2);
}
```

### Mengubah Font & Typography
Edit import fonts di `index.html` dan styling di `styles.css`

## 📱 Mobile Optimization

Game telah dioptimasi untuk mobile dengan:
- **Responsive sizing** untuk wheel
- **Touch-friendly buttons**
- **Optimized animations** untuk performa
- **Reduced particle effects** untuk battery saving

## 🔧 Troubleshooting

### Wheel Tidak Berputar
- Pastikan JavaScript enabled
- Check browser console untuk error
- Refresh halaman untuk reload

### GitHub Pages Tidak Load
- Pastikan repository Public
- Check branch dan folder settings
- Tunggu 5-10 menit untuk deployment

### Performance Issues
- Clear browser cache
- Check network connection
- Close other browser tabs

## 🎨 Design Features

### Color Scheme
- **Primary**: Gold gradient (#ffd700, #ffed4e)
- **Background**: Dark gradient (#1e1e2e, #2d1b69)
- **Accent**: Purple (#a78bfa)
- **Success**: Green (#4ade80)
- **Warning**: Red (#ff6b6b)

### Typography
- **Headers**: Orbitron (futuristic)
- **Body**: Roboto (readable)
- **Weight**: Bold untuk emphasis

### Animations
- **Spin Duration**: 3 detik dengan easing
- **Confetti**: 50 pieces, berbagai warna
- **Stats Animation**: 1 detik counter animation

## 📈 Future Enhancements

Ideas untuk development selanjutnya:
- **Multiplayer Mode**: Spin dengan teman
- **Prize Pool**: Daily/weekly rewards
- **Achievement System**: Badge collection
- **Social Sharing**: Share results
- **Custom Themes**: Multiple visual styles
- **Soundtrack**: Background music
- **More Items**: Expanded item database

## 📄 License

This project is open source. Feel free to modify and distribute.

---

**Selamat bermain di LootDungeon!** 🎰✨

Developed by MiniMax Agent - 2025