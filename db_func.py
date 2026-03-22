import sqlite3
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd

logger = logging.getLogger("AlumniETL.db")


def ensure_alumni_table(
    db_name: str = "JAA.db",
    sql_path: str | None = None,
) -> None:
    """
    若数据库文件不存在则自动创建；若尚无 alumni 表，则执行 query.sql 中
    -- @name: create_alumni_table 对应的建表语句。
    """
    db_path = Path(db_name)
    if sql_path is None:
        sql_file = Path(__file__).resolve().parent / "query.sql"
    else:
        sql_file = Path(sql_path)

    if not sql_file.is_file():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    queries = get_query_dict(str(sql_file))
    key = "create_alumni_table"
    if key not in queries or not queries[key].strip():
        raise ValueError(f"Named query '{key}' missing or empty in {sql_file}")

    create_sql = queries[key].strip()

    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
            ("alumni",),
        )
        if cur.fetchone() is None:
            cur.execute(create_sql)
            conn.commit()
            logger.info("Created table 'alumni' in %s", db_path)
        else:
            logger.debug("Table 'alumni' already exists in %s", db_path)

def write_df_to_db(df, db_name='JAA.db', table_name='alumni'):
    # write dataframe to db
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name,conn, if_exists='append', index=False)
    conn.close()

def read_from_db(query, db_name='JAA.db'): # query data using pd method
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def query_data(query, db_name='JAA.db'): # query data using normal method
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
    
def execute_query(query, params=None, db_name='JAA.db'):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # 判断是单条数据还是多条数据
        if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params or ())
            
        conn.commit() # 显式 commit 也是好习惯
        logger.info("Successfully execute query!")

def get_query_dict(sql_file):
    queries = {}
    current_name = None
    with open(sql_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('-- @name:'):
                current_name = line.split(':')[1].strip()
                queries[current_name] = ""
            elif current_name and line.strip() and not line.startswith('--'):
                queries[current_name] += line
    return queries

def load_to_db(df, table_name="alumni", db_path='JAA.db'):
    if df.empty:
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

def sync_df_to_db_cleanly(df, db_path='JAA.db'):
    if df.empty:
        return
    
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        df.to_sql("temp_alumni", conn, if_exists='replace', index=False)
        sync_sql = text("""
            INSERT OR IGNORE INTO alumni(linkedin_url,full_name,location,about,cur_role,experience,education,contact_info,shared_connections,skills,languages,num_conn,yrs_at_cur,yrs_aft_grad)
            SELECT linkedin_url,full_name,location,about,cur_role,experience,education,contact_info,shared_connections,skills,languages,num_conn,yrs_at_cur,yrs_aft_grad 
            FROM temp_alumni
                        """)
        result = conn.execute(sync_sql)
        conn.execute(text("DROP TABLE IF EXISTS temp_alumni;"))
    logger.info(f"Data Sync to database successful!")

def get_fieldnames(table_name): # Return a list of all fieldnames
    table_name_q = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    q_list = query_data(table_name_q)
    if len(q_list) == 1:
        field_name_q = f"PRAGMA table_info({table_name})"
        temp_df = read_from_db(field_name_q)
        result = temp_df['name'].tolist()
        return result
    else:
        logger.error('get_fildnames: Invalid table_name!')




