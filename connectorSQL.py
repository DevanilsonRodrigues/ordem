import pyodbc

try:
    def get_db_connection():
        # Dados de conexão
        server = 'testesql-azure.database.windows.net'
        database = 'sqldatabase'
        username = 'JuliaNovaisSQL@testesql-azure.database.windows.net'
        password = 'Juli@2021'

        # String de conexão (Removido ,1433 do SERVER)
        connection_string = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={server},1433;'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f'Encrypt=yes;'
            f'TrustServerCertificate=no;'
            f'Connection Timeout=30;'
        )
        return pyodbc.connect(connection_string)

    # Função para salvar dados no banco de dados
    def save_to_db(order_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO orders (order_id, description, cost_center, cost_responsible, division, center, company, [user], status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, order_data)

        conn.commit()
        cursor.close()
        conn.close()

        return cursor.rowcount > 0

    # Função para buscar todos os usuários
    def get_users_from_db():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT [user] FROM orders")

        users = [user[0] for user in cursor.fetchall()]
        cursor.close()
        conn.close()
        return users

    # Função para criar um novo usuário
    def create_user(user):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insere um novo usuário (ajuste os campos conforme sua tabela)
            cursor.execute("""
            INSERT INTO orders ([user], status)
            VALUES (?, ?)
            """, (user, 'Novo'))

            conn.commit()
            print(f"✅ Usuário '{user}' criado com sucesso.")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    # Função para verificar se um usuário existe ou criar um novo
    def ensure_user_exists(user):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o usuário já existe
        cursor.execute("SELECT TOP 1 1 FROM orders WHERE [user] = ?", (user,))
        exists = cursor.fetchone() is not None

        if not exists:
            print(f"🔍 Usuário '{user}' não encontrado. Criando novo usuário...")
            create_user(user)  # Cria um novo usuário se não existir

        cursor.close()
        conn.close()

        return True




    # Função para buscar ordens filtradas por usuário
    def get_orders_by_user(user=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        if user:
            cursor.execute("SELECT * FROM orders WHERE [user] = ?", (user,))
        else:
            cursor.execute("SELECT * FROM orders")

        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return orders

    def delete_order(order_id):
        # Lógica para excluir a ordem do banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE order_id = %s', (order_id,))
        conn.commit()
        cursor.close()
        conn.close()


    # Função para atualizar o status de uma ordem
    def update_order_status(order_id, status):
        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = "UPDATE orders SET status = ? WHERE order_id = ?"
        cursor.execute(update_query, (status, order_id))

        conn.commit()
        cursor.close()
        conn.close()

        return cursor.rowcount > 0
    
    def get_all_orders():
        conn = get_db_connection()  # Sua função de conexão
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")  # Ajuste conforme o nome da sua tabela
        results = cursor.fetchall()
        conn.close()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in results]


except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
