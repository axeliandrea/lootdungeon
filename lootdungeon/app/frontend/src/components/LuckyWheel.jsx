import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Ticket, Trophy, TrendingUp, User, Sparkles } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PRIZE_COLORS = [
  "#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6",
  "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#a855f7"
];

const LuckyWheel = () => {
  const [telegramId, setTelegramId] = useState("");
  const [user, setUser] = useState(null);
  const [prizes, setPrizes] = useState([]);
  const [spinning, setSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const [history, setHistory] = useState([]);
  const wheelRef = useRef(null);
  const [showLogin, setShowLogin] = useState(true);

  useEffect(() => {
    fetchPrizes();
  }, []);

  useEffect(() => {
    if (user) {
      fetchHistory();
    }
  }, [user]);

  const fetchPrizes = async () => {
    try {
      const response = await axios.get(`${API}/prizes`);
      setPrizes(response.data.prizes);
    } catch (error) {
      console.error("Error fetching prizes:", error);
    }
  };

  const fetchUser = async (id) => {
    try {
      const response = await axios.get(`${API}/user/${id}`);
      setUser(response.data);
      setShowLogin(false);
      toast.success(`Welcome, ${response.data.first_name || 'User'}!`);
    } catch (error) {
      toast.error("User not found. Please start the bot first!");
    }
  };

  const fetchHistory = async () => {
    if (!user) return;
    try {
      const response = await axios.get(`${API}/history/${user.telegram_id}`);
      setHistory(response.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (telegramId) {
      fetchUser(telegramId);
    }
  };

  const createConfetti = () => {
    for (let i = 0; i < 50; i++) {
      const confetti = document.createElement('div');
      confetti.className = 'confetti';
      confetti.style.left = Math.random() * 100 + '%';
      confetti.style.background = PRIZE_COLORS[Math.floor(Math.random() * PRIZE_COLORS.length)];
      confetti.style.animationDelay = Math.random() * 0.5 + 's';
      document.body.appendChild(confetti);
      
      setTimeout(() => confetti.remove(), 3000);
    }
  };

  const spinWheel = async () => {
    if (!user) {
      toast.error("Please login first!");
      return;
    }

    if (user.tickets < 1) {
      toast.error("You don't have enough tickets!");
      return;
    }

    if (spinning) return;

    setSpinning(true);

    try {
      const response = await axios.post(`${API}/spin`, {
        telegram_id: user.telegram_id
      });

      if (response.data.success) {
        const prize = response.data.prize;
        const prizeIndex = prizes.indexOf(prize);
        const segmentAngle = 360 / prizes.length;
        const targetAngle = segmentAngle * prizeIndex;
        const randomSpins = 5 + Math.random() * 3;
        const totalRotation = randomSpins * 360 + (360 - targetAngle) + segmentAngle / 2;
        
        const newRotation = rotation + totalRotation;
        setRotation(newRotation);

        if (wheelRef.current) {
          wheelRef.current.style.setProperty('--spin-degrees', `${totalRotation}deg`);
          wheelRef.current.style.setProperty('--spin-duration', '5s');
          wheelRef.current.classList.add('spinning');
        }

        setTimeout(() => {
          setSpinning(false);
          if (wheelRef.current) {
            wheelRef.current.classList.remove('spinning');
          }
          
          // Update user tickets
          setUser(prev => ({
            ...prev,
            tickets: response.data.remaining_tickets,
            total_spins: (prev.total_spins || 0) + 1
          }));

          // Show success with confetti
          createConfetti();
          toast.success(
            <div className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              <span className="font-bold">{prize}</span>
            </div>,
            {
              duration: 5000,
            }
          );
          
          fetchHistory();
        }, 5000);
      } else {
        setSpinning(false);
        toast.error(response.data.message);
      }
    } catch (error) {
      setSpinning(false);
      toast.error("Error spinning the wheel. Please try again.");
    }
  };

  const handleLogout = () => {
    setUser(null);
    setShowLogin(true);
    setTelegramId("");
    setHistory([]);
  };

  if (showLogin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 via-pink-500 to-red-500 flex items-center justify-center p-4">
        <Card className="w-full max-w-md glass border-white/20" data-testid="login-card">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                <Sparkles className="h-10 w-10 text-white" />
              </div>
            </div>
            <CardTitle className="text-3xl font-bold text-white">
              🎰 Lucky Wheel
            </CardTitle>
            <p className="text-white/80 mt-2">Enter your Telegram ID to start spinning!</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="telegram-id" className="text-white font-medium">
                  Telegram ID
                </Label>
                <Input
                  id="telegram-id"
                  type="number"
                  placeholder="Enter your Telegram ID"
                  value={telegramId}
                  onChange={(e) => setTelegramId(e.target.value)}
                  required
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  data-testid="telegram-id-input"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-bold py-6 rounded-xl btn-primary"
                data-testid="login-button"
              >
                Start Playing 🎮
              </Button>
            </form>
            <div className="mt-6 p-4 bg-white/10 rounded-lg border border-white/20">
              <p className="text-white/90 text-sm">
                <strong>How to get your Telegram ID:</strong><br/>
                1. Start our bot @dhloot_bot<br/>
                2. Send /start command<br/>
                3. Your ID will be in your profile
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 py-8 px-4" data-testid="lucky-wheel-page">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-2" style={{ fontFamily: 'Space Grotesk' }}>
            🎰 Lucky Wheel Roulette
          </h1>
          <p className="text-white/80 text-lg">Spin the wheel and win amazing prizes!</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="glass border-white/20" data-testid="user-stats-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/60 text-sm font-medium">Player</p>
                  <p className="text-white text-xl font-bold">{user?.first_name || user?.username || 'User'}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-white/20" data-testid="tickets-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/60 text-sm font-medium">Tickets</p>
                  <p className="text-white text-3xl font-bold">{user?.tickets || 0}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                  <Ticket className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-white/20" data-testid="spins-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white/60 text-sm font-medium">Total Spins</p>
                  <p className="text-white text-3xl font-bold">{user?.total_spins || 0}</p>
                </div>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Wheel Section */}
          <div className="lg:col-span-2">
            <Card className="glass border-white/20 p-8" data-testid="wheel-card">
              <div className="wheel-container">
                <div className="wheel-pointer"></div>
                <div className="wheel" ref={wheelRef}>
                  {prizes.map((prize, index) => {
                    const angle = (360 / prizes.length) * index;
                    const skewAngle = -90 + 360 / prizes.length;
                    return (
                      <div
                        key={index}
                        className="wheel-segment"
                        style={{
                          transform: `rotate(${angle}deg) skewY(${skewAngle}deg)`,
                          background: PRIZE_COLORS[index]
                        }}
                      >
                        <span style={{
                          transform: `skewY(${-skewAngle}deg) rotate(${18}deg)`,
                          display: 'inline-block',
                          width: '100%',
                          textAlign: 'center'
                        }}>
                          {prize}
                        </span>
                      </div>
                    );
                  })}
                  <div className="wheel-center">🎯</div>
                </div>
              </div>

              <div className="mt-8 flex flex-col items-center gap-4">
                <Button
                  onClick={spinWheel}
                  disabled={spinning || !user || user.tickets < 1}
                  className="w-full max-w-md bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 hover:from-yellow-500 hover:via-orange-600 hover:to-red-600 text-white font-bold py-6 text-xl rounded-xl btn-primary shadow-2xl"
                  data-testid="spin-button"
                >
                  {spinning ? '🎰 Spinning...' : '🎲 SPIN THE WHEEL!'}
                </Button>
                
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className="border-white/20 text-white hover:bg-white/10"
                  data-testid="logout-button"
                >
                  Logout
                </Button>
              </div>
            </Card>
          </div>

          {/* History Section */}
          <div>
            <Card className="glass border-white/20" data-testid="history-card">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Trophy className="h-5 w-5" />
                  Recent Wins
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {history.length === 0 ? (
                    <p className="text-white/60 text-center py-8">No spins yet. Start playing!</p>
                  ) : (
                    history.map((item, index) => (
                      <div
                        key={index}
                        className="p-3 bg-white/10 rounded-lg border border-white/20 hover:bg-white/20 transition-colors"
                        data-testid={`history-item-${index}`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-white font-semibold">{item.prize}</span>
                          <span className="text-white/60 text-sm">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-white/20 mt-4" data-testid="info-card">
              <CardHeader>
                <CardTitle className="text-white text-lg">ℹ️ How to Play</CardTitle>
              </CardHeader>
              <CardContent className="text-white/80 text-sm space-y-2">
                <p>• Claim tickets from group giveaways</p>
                <p>• Earn points by chatting (5 chars = 1 point)</p>
                <p>• Buy tickets with points (25 points = 1 ticket)</p>
                <p>• Spin the wheel to win prizes!</p>
                <div className="mt-4 p-3 bg-white/10 rounded-lg border border-white/20">
                  <p className="text-white font-semibold mb-1">💰 Your Points</p>
                  <p className="text-white text-2xl font-bold">{user?.points || 0}</p>
                  <p className="text-white/60 text-xs mt-1">{Math.floor((user?.points || 0) / 25)} tickets available to buy</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LuckyWheel;
