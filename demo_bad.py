import os
import sqlite3

# This file is intentionally bad for testing the reviewer

def login(username, password):
    # CRITICAL: Hardcoded secret (fake)
    admin_token = "sk-live-12345thisisarealsecretkey"
    
    # CRITICAL: SQL Injection vulnerability
    # Also poor variable naming 'c'
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    query = "SELECT * FROM users WHERE user = '" + username + "' AND pass = '" + password + "'"
    c.execute(query)
    
    return c.fetchone()

def heavy_computation(data):
    # PERFORMANCE: Nested loops O(N^2)
    results = []
    for i in data:
        for j in data:
            if i == j:
                results.append(i)
                
    # QUALITY: Magic number
    if len(results) > 999:
        print("Too many")
        
    return results

class god_object:
    # QUALITY: Class name not Capitalized
    # QUALITY: Implicitly doing too much (if we added more methods)
    pass
