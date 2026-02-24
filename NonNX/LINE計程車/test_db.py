# 創建測試檔案 test_db.py
import psycopg2

# 先測試是否能建立連接，不執行任何查詢
try:
    conn = psycopg2.connect(
        host='db.zjwbzxfylzydmdzikvpd.supabase.co',
        port=5432,
        database='postgres', 
        user='postgres',
        password='mRx7coqcQD6Zq0UJ'
    )
    print("基本連接成功！")
    conn.close()
    
except Exception as e:
    print(f"連接失敗: {e}")
    print(f"錯誤類型: {type(e).__name__}")