from flask import jsonify
from connection.get_db_connection import get_db_connection
from utils.company_colors import company_colors

def get_company_list():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT figi_id, company_name FROM figi_numbers")
        rows = cur.fetchall()
        
        company_list = {
            row[1].lower(): {
                'id': row[0],
                'color': company_colors.get(row[1].lower(), 'linear-gradient(to right, #ffffff, #ffffff)')
            } for row in rows
        }
        
    finally:
        cur.close()
        conn.close()
    
    return jsonify(company_list)
