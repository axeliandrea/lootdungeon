#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script untuk Lucky Wheel Bot
"""

import sqlite3
import os
import time
import requests
import json
from bot import DatabaseManager

def test_database():
    """Test database functionality"""
    print("🗄️ Testing Database...")
    
    try:
        db = DatabaseManager("/workspace/test_bot_database.db")
        
        # Test user creation
        db.create_user(12345, "testuser", "Test User")
        user_data = db.get_user(12345)
        assert user_data is not None, "User creation failed"
        print("✅ User creation: OK")
        
        # Test inventory add
        db.add_prize_to_user(12345, "fizz_coin", 100)
        inventory = db.get_user_inventory(12345)
        assert inventory['fizz_coin'] == 100, "Inventory add failed"
        print("✅ Inventory add: OK")
        
        # Test prize deduction
        can_deduct = db.deduct_ticket(12345)
        assert can_deduct, "Ticket deduction failed"
        print("✅ Ticket deduction: OK")
        
        # Cleanup
        os.remove("/workspace/test_bot_database.db")
        print("✅ Database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_web_server():
    """Test web server availability"""
    print("🌐 Testing Web Server...")
    
    try:
        # Test if web server is running
        response = requests.get("http://localhost:8080", timeout=5)
        assert response.status_code == 200, "Web server not responding"
        print("✅ Web server response: OK")
        
        # Test lucky wheel page
        response = requests.get("http://localhost:8080/luckywheel.html", timeout=5)
        assert "Lucky Wheel" in response.text, "Lucky wheel page not found"
        print("✅ Lucky wheel page: OK")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Web server test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Web server test error: {e}")
        return False
    
    return True

def test_spin_api():
    """Test spin result API"""
    print("🎲 Testing Spin API...")
    
    try:
        test_data = {
            "user_id": 12345,
            "prize_type": "fizz_coin",
            "prize_value": 100,
            "prize_emoji": "💰 1x"
        }
        
        response = requests.post(
            "http://localhost:8080/api/spin-result",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200, "API not responding"
        
        result = response.json()
        assert result.get('success') == True, "API returned error"
        print("✅ Spin API: OK")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Spin API test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Spin API test error: {e}")
        return False
    
    return True

def test_bot_token():
    """Test bot token validity"""
    print("🤖 Testing Bot Token...")
    
    try:
        from bot import BOT_TOKEN
        assert BOT_TOKEN != "", "Bot token is empty"
        assert len(BOT_TOKEN.split(":")) == 2, "Bot token format invalid"
        print("✅ Bot token format: OK")
        
    except Exception as e:
        print(f"❌ Bot token test failed: {e}")
        return False
    
    return True

def check_ports():
    """Check if required ports are available"""
    print("🔌 Checking Ports...")
    
    import socket
    
    # Check port 8080 for web server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8080))
    if result == 0:
        print("✅ Port 8080 is in use (web server running)")
    else:
        print("⚠️ Port 8080 is free (web server not running)")
    sock.close()
    
    return True

def main():
    """Main test function"""
    print("🧪 Lucky Wheel Bot Test Suite")
    print("=" * 40)
    
    tests = [
        ("Database", test_database),
        ("Bot Token", test_bot_token),
        ("Port Check", check_ports),
        ("Web Server", test_web_server),
        ("Spin API", test_spin_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed!")
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot should be working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    main()