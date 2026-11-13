import os
import sys
import re

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

from app import app, get_db

application = app

try:
    conn = get_db()
    cursor = conn.cursor()
    
    sql_file = os.path.join(path, 'database.sql')
    if os.path.exists(sql_file):
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # تجاهل أوامر CREATE DATABASE و USE
        sql_content = re.sub(r'CREATE DATABASE.*?;', '', sql_content, flags=re.DOTALL)
        sql_content = re.sub(r'USE .*?;', '', sql_content, flags=re.DOTALL)
        
        for command in sql_content.split(';'):
            if command.strip():
                try:
                    cursor.execute(command)
                except Exception:
                    pass
        
        conn.commit()
        print("✅ تم التحقق من الجداول بنجاح")
    conn.close()
except Exception as e:
    print(f"⚠️ خطأ في إنشاء الجداول: {e}")
