import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from models.user_model import ClientCreation , Item, ItemEdit , ItemOrder , ItemCreate ,UserEdit ,farmerRegistration
from auth import hash_password , create_token
import datetime



load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn



def get_user_by_email(email:str)->dict[str] | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT user_id ,password, type  from "user" where email = %s""",(email,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            user_id , password, type = info
            return {'user_id':user_id,'email':email,'password':password,'type':type}
    finally:
        cursor.close()
        conn.close()
def get_user_by_id(user_id:str)->dict[str] | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT email ,password, type  from "user" where user_id = %s""",(user_id,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            email , password, type = info
            return {'user_id':user_id,'email':email,'password':password,'type':type}
    finally:
        cursor.close()
        conn.close()

def get_farmer_pid(id:int)->int | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT profile_id  from farmer_profile where user_id = %s""",(id,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            profile_id = int(info[0])
            return profile_id
    finally:
        cursor.close()
        conn.close()

def get_client_pid(id:int)->int | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT profile_id  from client_profile where user_id = %s""",(id,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            profile_id = int(info[0])
            return profile_id
    finally:
        cursor.close()
        conn.close()

def create_client(info: ClientCreation):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO "user"(email , password , type) VALUES(%s, %s, %s );""",
                          (info.email , hash_password(info.password) , info.type,))
        
        cursor.execute("""INSERT INTO client_profile(user_id,  Name, address)
                          SELECT user_id ,%s, %s FROM "user" WHERE email = %s """,
                           (info.name, info.address, info.email))
        
        conn.commit()
        user = get_user_by_email(info.email)
        return create_token(user['user_id'], user['type'])
    finally:
        cursor.close()
        conn.close()

def create_farmer(info: farmerRegistration):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO "user"(email , password , type) VALUES(%s, %s, %s );""",
                          (info.email , hash_password(info.password) , info.type,))
        
        cursor.execute("""INSERT INTO farmer_profile(user_id,  Name, address)
                          SELECT user_id ,%s, %s FROM "user" WHERE email = %s """,
                           (info.name, info.address, info.email))
        
        conn.commit()
        user = get_user_by_email(info.email)
        return create_token(user['user_id'], user['type'])
    finally:
        cursor.close()
        conn.close()  

def create_worker(info: farmerRegistration):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO "user"(email , password , type) VALUES(%s, %s, %s );""",
                          (info.email , hash_password(info.password) , info.type,))
        
        cursor.execute("""INSERT INTO worker_profile(user_id,  Name)
                          SELECT user_id ,%s FROM "user" WHERE email = %s """,
                           (info.name, info.email))
        
        conn.commit()
        user = get_user_by_email(info.email)
        return create_token(user['user_id'], user['type'])
    finally:
        cursor.close()
        conn.close()  

def add_to_stock(item_data : ItemCreate):    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO item_in_stock (profile_id , title , qty , price) VALUES(%s, %s, %s ,%s);""",
                          (item_data.profile_id , item_data.title , item_data.qty, item_data.price))
        conn.commit()
    finally:
        cursor.close()
        conn.close() 
    
def item_edit(item: ItemEdit):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if item.title:
             cursor.execute("""UPDATE item_in_stock SET title = %s WHERE item_id = %s;""",(item.title , item.id))
        if item.price:
             cursor.execute("""UPDATE item_in_stock SET price = %s WHERE item_id = %s;""",(item.price , item.id))
        if item.qty:
             cursor.execute("""UPDATE item_in_stock SET qty = %s WHERE item_id = %s;""",(item.qty , item.id))
        conn.commit()
        return {"message": "edit item successfully", "status": "ok"}
    finally:
        cursor.close()
        conn.close()
    
def validate_item_ownership(item_id:int ,profile_id: int )->bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute("""SELECT * FROM item_in_stock WHERE item_id = %s AND profile_id = %s;""",(item_id , profile_id))
        info = cursor.fetchone()
        if info is None:
            return False
        else:
            return True
    finally:
        cursor.close()
        conn.close()

def item_delete(item_id: int)-> dict[str] | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE item_in_stock SET profile_id = 2 WHERE item_id = %s """,(item_id,))
        conn.commit()
        return {"message": "item has been deleted successfully.", "status": "ok"}
    finally:
        cursor.close()
        conn.close() 

def place_order(client_id: int , items: list[ItemOrder], day : str , repeat : bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO "order"(profile_id , status , day , repeat) VALUES( %s, %s , %s , %s );""",
                          (client_id,"processing", day , repeat))
        for item in items:
            cursor.execute("""INSERT INTO order_item(order_id, farmer_id, item_id, order_qty)
                  VALUES((SELECT order_id FROM "order" ORDER BY order_time DESC LIMIT 1), %s, %s, %s)""",
               (item.farmer_id, item.item_id, item.qty))
            
        conn.commit()
        
        
    finally:
        cursor.close()
        conn.close()

def check_qty(item_id , order_qty:int) -> bool | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT qty  from item_in_stock where item_id = %s""",(item_id,))
        stock_qty = cursor.fetchone() # return a tuple or None
        if stock_qty is None:
            return None
        else:
            stock_qty = int(stock_qty[0])
            return (stock_qty >= order_qty)
    finally:
        cursor.close()
        conn.close()
    
def get_farmer_pid_by_item(id:int)->int | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT profile_id  from item_in_stock where item_id = %s""",(id,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            profile_id = int(info[0])
            return profile_id
    finally:
        cursor.close()
        conn.close()

def subtract_from_stock(item_id: int , qty: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE item_in_stock SET qty = qty - %s  WHERE item_id = %s""",(qty,item_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    
def items_in_stock()-> list[Item]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT profile_id ,title , qty, price, item_id   from item_in_stock WHERE qty != 0 AND profile_id != 2""")
        items = cursor.fetchall()# return a tuple or None
        item_list = list()
        
        if items is None:
            return None
        else:
            for item in items:
                item_list.append(Item(profile_id= item[0],title=item[1], qty= item[2], price=item[3] , item_id=item[4]))
        return item_list
    finally:
        cursor.close()
        conn.close()

def get_item_by_farmer(farmer_id: int ):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT  profile_id ,title , qty, price ,item_id  from item_in_stock WHERE profile_id = %s""",(farmer_id,))
        items = cursor.fetchall()# return a tuple or None
        item_list = list()
        
        if items is None:
            return None
        else:
            for item in items:
                item_list.append(Item( profile_id= item[0],title=item[1], qty= item[2], price=item[3],item_id=item[4]))
        return item_list
    finally:
        cursor.close()
        conn.close()

def order_by_client(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT  status ,order_time , day, repeat, order_id  from "order" WHERE profile_id = %s""",(client_id,))
        orders = cursor.fetchall()# return a tuple or None
        order_list = list()
        if orders is None:
            return None
        else:
            for order in orders:
                order_list.append({"status": str(order[0]),"order_time":str(order[1]), "day": str(order[2]), "repeat":str(order[3]) , "order_id":str(order[4])})
        return order_list
    finally:
        cursor.close()
        conn.close()

def order_by_item(item_id:int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT order_time , day, repeat, order_item.order_id FROM order_item LEFT JOIN "order" ON "order".order_id = order_item.order_id WHERE item_id = %s;""",(item_id,))
        orders = cursor.fetchall()# return a tuple or None
        order_list = list()
        if orders is None:
            return None
        else:
            for order in orders:
                order_list.append({"status": str(order[0]),"order_time":str(order[1]), "day": str(order[2]), "repeat":str(order[3]) , "order_id":str(order[4])})
        return order_list
    finally:
        cursor.close()
        conn.close()

    
def order_items(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT  profile_id ,title , order_item.order_qty, price ,item_in_stock.item_id  from item_in_stock LEFT JOIN order_item ON item_in_stock.item_id = order_item.item_id WHERE order_id = %s""",(int(order_id),))
        items = cursor.fetchall()# return a tuple or None
        item_list = list()
        
        if items is None:
            return None
        else:
            for item in items:
                item_list.append(Item( profile_id= item[0],title=item[1], qty= item[2], price=item[3],item_id=item[4]))
        return item_list
    finally:
        cursor.close()
        conn.close()

def order_items_by_farmer(profile_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT 
                            i.title, 
                            o.day, 
	                        oi.order_qty
                        FROM 
                            "order" AS o
                        INNER JOIN 
                            order_item AS oi ON o.order_id = oi.order_id
                        INNER JOIN 
                            item_in_stock AS i ON oi.item_id = i.item_id WHERE farmer_id = %s""",(int(profile_id),))
        orders = cursor.fetchall()# return a tuple or None
        order_list = list()
        
        if orders is None:
            return None
        else:
            for item in orders:
                order_list.append({"title":str( item[0]),"day":str(item[1]), "qty":str(item[2])})
        return order_list
    finally:
        cursor.close()
        conn.close()
    
def order_cancel(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE "order" SET status = 'canceled' WHERE order_id = %s """,(order_id,))
        conn.commit()
        return {"message": "item has been deleted successfully.", "status": "ok"}
    finally:
        cursor.close()
        conn.close()

def validate_order_ownership(order_id:int ,profile_id: int )->bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute("""SELECT * FROM "order" WHERE order_id = %s AND profile_id = %s;""",(order_id , profile_id))
        info = cursor.fetchone()
        if info is None:
            return False
        else:
            return True
    finally:
        cursor.close()
        conn.close()

def edit_user(user: UserEdit , user_id: int ,type : str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if type == 'farmer':
            if user.name:
             cursor.execute("""UPDATE farmer_profile SET name = %s WHERE user_id = %s;""",( user.name, user_id))
            if user.address:
             cursor.execute("""UPDATE farmer_profile SET address = %s WHERE user_id = %s;""",(user.address , user_id))
            if user.email:
             cursor.execute("""UPDATE "user" SET email = %s WHERE user_id = %s;""",(user.email , user_id))
            conn.commit()
        
        if type == 'client':
            if user.name:
             cursor.execute("""UPDATE client_profile SET name = %s WHERE user_id = %s;""",( user.name, user_id))
            if user.address:
             cursor.execute("""UPDATE client_profile SET address = %s WHERE user_id = %s;""",(user.address , user_id))
            if user.email:
             cursor.execute("""UPDATE "user" SET email = %s WHERE user_id = %s;""",(user.email , user_id))
            conn.commit()

        return {"message": "edit profile successfully", "status": "ok"}
    finally:
        cursor.close()
        conn.close()

def get_today_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    current_weekday = now.strftime("%A")
    try:
        cursor.execute("""SELECT  status ,order_time , day, repeat, order_id, profile_id  from "order" WHERE  day = %s """,(current_weekday.lower(),))
        orders = cursor.fetchall()
        order_list = list()
        if orders is None:
            return None
        else:
            for order in orders:
                order_list.append({"status": str(order[0]),"order_time":str(order[1]), "day": str(order[2]), "repeat":str(order[3]) , "order_id":str(order[4]) ,"profile_id":str(order[5] )})
        return order_list
    finally:
        cursor.close()
        conn.close()

def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    try:
        cursor.execute("""SELECT  status ,order_time , day, repeat, order_id, profile_id  from "order" """)
        orders = cursor.fetchall()
        order_list = list()
        if orders is None:
            return None
        else:
            for order in orders:
                order_list.append({"status": str(order[0]),"order_time":str(order[1]), "day": str(order[2]), "repeat":str(order[3]) , "order_id":str(order[4]) ,"profile_id":str(order[5] )})
        return order_list
    finally:
        cursor.close()
        conn.close()

def edit_order_status(order_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        
        cursor.execute("""UPDATE "order" SET status = %s WHERE order_id = %s;""",(status.lower() , order_id,))
        
        conn.commit()
        return {"message": "edit order successfully", "status": "ok"}
    finally:
        cursor.close()
        conn.close()
    
def account_info(id: int,type : str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if type == 'client':
            cursor.execute("""SELECT name , address , email  from client_profile LEFT JOIN "user" ON "user".user_id = client_profile.user_id WHERE "user".user_id = %s""",(id,))
        else:
            cursor.execute("""SELECT name , address , email  from farmer_profile LEFT JOIN "user" ON "user".user_id = farmer_profile.user_id WHERE "user".user_id = %s""",(id,))
        info = cursor.fetchone() # return a tuple or None
        if info is None:
            return None
        else:
            account = {"name":str(info[0]),"address":str(info[1]), "email": str(info[2])}
            return account
    finally:
        cursor.close()
        conn.close()

def edit_password(password: str , user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    password =  hash_password(password)
    try:
        cursor.execute("""UPDATE "user" SET password = %s  WHERE user_id = %s""",(password, user_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def farmer_revenue(profile_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        
        cursor.execute("""SELECT 
                            i.title, 
                            TO_CHAR(o.order_time, 'YYYY-MM-DD') as time_str,
	                        oi.order_qty,
                            i.price
                        FROM 
                            "order" AS o
                        INNER JOIN 
                            order_item AS oi ON o.order_id = oi.order_id
                        INNER JOIN 
                            item_in_stock AS i ON oi.item_id = i.item_id WHERE oi.farmer_id = %s""",(profile_id,))
        
        infos = cursor.fetchall() # return a tuple or None
        items = list()
        if infos is None:
            return None
        else:
         for info in infos:
                items.append({"title":str(info[0]),"time":str(info[1]), "qty": str(info[2]) , "price": str(info[3])})
        return items
    finally:
        cursor.close()
        conn.close()

def admin_revenue():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        
        cursor.execute("""SELECT 
                            i.title, 
                            TO_CHAR(o.order_time, 'YYYY-MM-DD') as time_str,
	                        oi.order_qty,
                            i.price
                        FROM 
                            "order" AS o
                        INNER JOIN 
                            order_item AS oi ON o.order_id = oi.order_id
                        INNER JOIN 
                            item_in_stock AS i ON oi.item_id = i.item_id """)
        
        infos = cursor.fetchall() # return a tuple or None
        items = list()
        if infos is None:
            return None
        else:
         for info in infos:
                items.append({"title":str(info[0]),"time":str(info[1]), "qty": str(info[2]) , "price": str(info[3])})
        return items
    finally:
        cursor.close()
        conn.close()