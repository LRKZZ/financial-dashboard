from flask import jsonify
from connection.get_db_connection import get_db_connection


def search_company(query):
    if query:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT figi_id, company_name 
            FROM figi_numbers 
            WHERE company_name ILIKE %s
            LIMIT 10;
        """,
            (f"%{query}%",),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        results = [{"figi_id": row[0], "company_name": row[1]} for row in rows]
        return jsonify(results)
    return jsonify([])
