import os 
import requests
import config,cryption
import json
import sqlite3
import struct
import base64
import ctypes

output_dir = "./"
libc = ctypes.cdll.LoadLibrary("./src/bisque/BisquseDLL.dll")
libc.CreateFromKey.argtypes = [ctypes.c_char_p]
libc.CreateFromKey.restype = ctypes.c_void_p
libc.Decrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
libc.Decrypt.restype = ctypes.c_int
libc.Encrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
libc.Encrypt.restype = ctypes.c_char_p
libc.ReleaseBuffer.argtypes = [ctypes.c_char_p]
libc.ReleaseInst.argtypes = [ctypes.c_void_p]


#check la version actuelle de la database avec le fichier ressource
def check_resources():
    url = config.get_version() + "/resources/resource_list_path.json"
    r = config.session.get(url, headers=config.session.headers)
    decoded = cryption.Decrypt(config.get_session_key(), r.json()['data'])
    decoded = json.loads(decoded.value.decode('utf-8'))
    #url de la ressource 
    database_url = decoded['resource_list_uri']
    
    #nom du fichier 
    filename = database_url.split('/')[-1]
    version = filename.split("_")[0]
    if not os.path.isfile("./sakura.db"):
        #dl du fichié avec le nom dans filename
        with open(version , "wb") as ressource:
            ressource.write(requests.get(database_url).content)

        #decrypt nty
        k = cryption.CreateFromKey("J6oxF6iN")
        dec = cryption.Nty_decryptor(k,version,".nty")

        #delete le fichier
        os.remove(version)

        with open(dec) as input_file:
            data = json.load(input_file)
            urls = []
            for resource in data['resources']:
                resource_type = resource.get('type')
                if resource_type in ["sqlite_database"]:
                    url = resource.get('url')
                    name = resource.get('name')
                    result = url + '/' + name
                    if url:
                        urls.append(result)
        return urls
    else:
        conn = sqlite3.connect('./sakura.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Version'")
        table_exists = cursor.fetchone()
        if not table_exists:
            print("Database outdated! Updating database...")
            conn.close()
            os.remove("sakura.db")
            check_database()
        else: 
            cursor.execute("SELECT * FROM Version")
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == version:
                    print("Database is up to date !")
                    return None
                else:
                    print("Updating database...")
                    conn.close()
                    os.remove("sakura.db")
                    check_database()

#dl les databases avec les urls recupérées dans ressource
def check_database():
    #dl des databases
    urls = check_resources()
    if urls == None:
        return 0
    else:
        for url in urls:
            filename = url.split('/')[-1]
            name = filename.split("-")[0] + ".nty"
            filepath = os.path.join(output_dir, name)
            response = requests.get(url)
            if response.status_code == 200:
                with open(filepath, 'wb') as file:
                    file.write(response.content)
                    k = cryption.CreateFromKey("J6oxF6iN")
                    dec = cryption.Nty_decryptor(k,name,None)
            else:
                print(f"Failed to download the file {name}.")
        process_files()


#decryption des databases
def process_files():
    key = "JGcu2DjohFm84viZHe1Et5Qt"
    keydata = libc.CreateFromKey(key.encode('utf-8'))
    def read_header(fh):
        magic, rest_of_header = struct.unpack('<4s12s', fh.read(16))
        assert(magic == b'IKMN')

    def read_map_tables(fh):
        tables_crypted, = struct.unpack('<512s', fh.read(512))
        tables_crypted_b64 = base64.b64encode(tables_crypted)
        tables = ctypes.pointer(ctypes.c_char())
        decrypted_len = libc.Decrypt(keydata, tables_crypted_b64, ctypes.byref(tables))
        assert(decrypted_len == 512)

        enc_map = bytearray(256)
        dec_map = bytearray(256)
        enc_map[:] = tables[  0:256]
        dec_map[:] = tables[256:512]
        libc.ReleaseBuffer(tables)
        return enc_map, dec_map

    def remap_block(the_map, original):
        mapped = bytearray(len(original))
        for i in range(len(original)):
            mapped[i] = the_map[original[i]]
        return mapped

    def dec_db(db_encrypted, db_decrypted):
        with open(db_encrypted, mode="rb") as fh_encrypted:
            with open(db_decrypted, mode="wb") as fh_decrypted:
                read_header(fh_encrypted)
                enc_map, dec_map = read_map_tables(fh_encrypted)
                while True:
                    coded = fh_encrypted.read(8192)
                    if coded == b'':
                        break
                    decoded = remap_block(dec_map, coded)
                    fh_decrypted.write(decoded)

        # Renommer les fichiers de sortie
        dir_name = os.path.dirname(db_encrypted)
        file_name = os.path.basename(db_encrypted)
        file_name = file_name.replace('.nty', '.db')

        index = 1
        new_file_name = os.path.join(dir_name, file_name)
        while os.path.exists(new_file_name):
            index += 1
            new_file_name = os.path.join(dir_name, f'sakura_master_db_{index:03}.db')

        os.rename(db_decrypted, new_file_name)

    # Recherche des fichiers correspondants au modèle
    files = []
    for file in os.listdir('.'):
        if file.startswith('Sakura') and file.endswith('.nty'):
            files.append(file)

    for file in files:
        db_encrypted = file
        db_decrypted = db_encrypted.replace('.nty', '.db')

        dec_db(db_encrypted, db_decrypted)
        os.remove(db_encrypted)
    migrate_databases()

#migration des databases dans sakura.db
def migrate_databases():
    # Ouvrir une connexion à la base de données de destination
    # Chemin vers la base de données de destination
    destination_db_path = './sakura.db'
    # Chemins vers les bases de données sources
    source_db_paths = ['./sakura_master_db_002.db' , './sakura_master_db_003.db','./sakura_master_db_004.db','./sakura_master_db_005.db','./sakura_master_db_006.db','./sakura_master_db_007.db','./sakura_master_db_008.db','./sakura_master_db_009.db','./sakura_master_db_010.db','./sakura_master_db_011.db']
    
    destination_conn = sqlite3.connect(destination_db_path)
    destination_cursor = destination_conn.cursor()
    # Pour chaque base de données source
    for source_db_path in source_db_paths:
        # Ouvrir une connexion à la base de données source
        source_conn = sqlite3.connect(source_db_path)
        source_cursor = source_conn.cursor()

        # Récupérer la liste des tables dans la base de données source
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = source_cursor.fetchall()

        # Pour chaque table dans la base de données source
        for table in tables:
            table_name = table[0]

            # Supprimer la table existante dans la base de données de destination, si elle existe
            destination_cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

            # Récupérer le schéma de la table source
            source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            create_table_query = source_cursor.fetchone()[0]

            # Créer la table de destination
            destination_cursor.execute(create_table_query)

            # Copier les données de la table source vers la table de destination
            source_cursor.execute(f"SELECT * FROM {table_name};")
            rows = source_cursor.fetchall()
            for row in rows:
                placeholders = ', '.join(['?'] * len(row))
                insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                destination_cursor.execute(insert_query, row)

            # Récupérer les index de la table source
            source_cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';")
            indexes = source_cursor.fetchall()

            # Créer les index dans la base de données de destination
            for index in indexes:
                index_name = index[0]
                create_index_query = index[1]
                destination_cursor.execute(create_index_query)

        # Fermer la connexion à la base de données source
        source_conn.close()

    # Valider les modifications et fermer la connexion à la base de données de destination
    destination_conn.commit()
    destination_conn.close()
    
    #supprimer les db dans source_db_paths
    for delete in source_db_paths:
        os.remove(delete)

    for file in os.listdir('.'):
        if file.endswith('.nty'):
            ver = ''.join(filter(str.isdigit, file))
            # Se connecter à la base de données SQLite
            conn = sqlite3.connect('./sakura.db')
            cursor = conn.cursor()

            # Créer la table "Versions"
            cursor.execute('''CREATE TABLE IF NOT EXISTS Version
                  (Version TEXT)''')

            # Insérer les chiffres extraits dans la table
            cursor.execute("INSERT INTO Version VALUES (?)", (ver,))

            # Valider les modifications et fermer la connexion
            conn.commit()
            conn.close()
            
            os.remove(file)
