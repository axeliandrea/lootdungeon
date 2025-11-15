"""
Flask Web Application for LootDungeon Bot
Handles web interface and Telegram webhook
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import random
from datetime import datetime
from config import LUCKY_WHEEL_PRIZES, TICKET_COST_PER_SPIN, OWNER_ID
from database import Database

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    """Main index page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>LootDungeon Bot</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .info {
                color: #666;
                margin-bottom: 30px;
                line-height: 1.6;
            }
            .bot-link {
                display: inline-block;
                background: #0088cc;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: bold;
                transition: background 0.3s;
            }
            .bot-link:hover {
                background: #006699;
            }
            .features {
                margin-top: 30px;
                text-align: left;
            }
            .feature {
                margin: 10px 0;
                padding: 10px;
                background: #f5f5f5;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 LootDungeon Bot</h1>
            <div class="info">
                <p>Welcome to LootDungeon! Spin the lucky wheel and win amazing prizes.</p>
                <p>Use the bot on Telegram to play and manage your inventory.</p>
            </div>
            <a href="https://t.me/your_bot_username" class="bot-link">🤖 Open Bot on Telegram</a>
            <div class="features">
                <h3>🎰 Game Features:</h3>
                <div class="feature">💰 Win Fizz Coins (5% chance)</div>
                <div class="feature">🎫 Get Lucky Tickets (90% chance)</div>
                <div class="feature">🧪 Collect Potion HP (4% chance)</div>
                <div class="feature">☠️ Try your luck with Zonk (1% chance)</div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/luckywheel')
def luckywheel():
    """Lucky Wheel interface"""
    return render_template('lucky_wheel.html')

@app.route('/api/spin')
def api_spin():
    """API endpoint for spinning the wheel"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
    
    # Check if user has enough tickets (owner gets unlimited)
    player = db.get_player(user_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    # Owner gets unlimited tickets
    if user_id != OWNER_ID:
        if player['tickets'] < TICKET_COST_PER_SPIN:
            return jsonify({'error': 'Not enough tickets'}), 400
        # Use tickets
        db.use_tickets(user_id, TICKET_COST_PER_SPIN)
    
    # Generate random prize based on rates
    rand = random.randint(1, 100)
    cumulative_rate = 0
    
    selected_prize = None
    for prize_key, prize_data in LUCKY_WHEEL_PRIZES.items():
        cumulative_rate += prize_data['rate']
        if rand <= cumulative_rate:
            selected_prize = {
                'type': prize_key,
                'name': prize_data['name'],
                'emoji': prize_data['emoji'],
                'quantity': prize_data['amount']
            }
            break
    
    if not selected_prize:
        # Fallback to lowest rate prize
        selected_prize = {
            'type': 'zonk',
            'name': LUCKY_WHEEL_PRIZES['zonk']['name'],
            'emoji': LUCKY_WHEEL_PRIZES['zonk']['emoji'],
            'quantity': LUCKY_WHEEL_PRIZES['zonk']['amount']
        }
    
    # Add item to inventory
    prize_data = LUCKY_WHEEL_PRIZES[selected_prize['type']]
    db.add_item(user_id, selected_prize['type'], selected_prize['name'], 
                selected_prize['emoji'], selected_prize['quantity'])
    
    # Add coins if prize is coin
    if selected_prize['type'] == 'coin':
        db.add_coins(user_id, selected_prize['quantity'])
    
    # Log spin
    db.log_spin(user_id, selected_prize['type'], selected_prize['name'], 
                selected_prize['emoji'], selected_prize['quantity'])
    
    # Get updated player info
    updated_player = db.get_player(user_id)
    
    return jsonify({
        'success': True,
        'prize': selected_prize,
        'player_tickets': updated_player['tickets'] if updated_player else 0,
        'player_coins': updated_player['coins'] if updated_player else 0
    })

@app.route('/api/player/<int:user_id>')
def api_player(user_id):
    """Get player information"""
    player = db.get_player(user_id)
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    items = db.get_player_items(user_id)
    
    return jsonify({
        'player': player,
        'items': items
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    update = request.get_json()
    
    if not update:
        return '', 200
    
    # Handle the update (this will be processed by the bot)
    # The bot will also be listening to the same updates
    # For now, just acknowledge
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)