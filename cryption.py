import ctypes


libc = ctypes.cdll.LoadLibrary("./src/bisque/BisquseDLL.dll")

# ici les déclarations de typage des fonctions
libc.CreateFromKey.argtypes = [ctypes.c_char_p]
libc.CreateFromKey.restype = ctypes.c_void_p
libc.Decrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
libc.Decrypt.restype = ctypes.c_int
libc.Encrypt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
libc.Encrypt.restype = ctypes.c_char_p
libc.ReleaseBuffer.argtypes = [ctypes.c_char_p]
libc.ReleaseInst.argtypes = [ctypes.c_void_p]
libc.DecryptNTY.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_bool]
libc.DecryptNTY.restype = ctypes.c_int

def CreateFromKey(k):
    try:       
        """
        return: pointer to a MD159 ("inst" used in all functions below)

        """
        return libc.CreateFromKey(k.encode('utf-8'))
    except TypeError:
        pass
    except Exception as e:
        pass
        

def Decrypt(k, DataToDecrypt):
    decrypted = None
    try:       
        """
        Decrypted doit être une référence (que la fonction Decrypt va écrire avec un pointeur (tableau) valide à utiliser)
        """
        decrypted = ctypes.c_char_p()
        libc.Decrypt(k, DataToDecrypt.encode('utf-8'),  ctypes.byref(decrypted))
        
        return decrypted
    except TypeError:
        pass
    except Exception as e:
        pass
        # Il faut toujours libérer le tampon "decrypted" donné par la fonction Decrypt
        
def Encrypt(k, DataToEncrypt):
    encrypted = None
    try:       
        """
        Decrypted doit être une référence (que la fonction Decrypt va écrire avec un pointeur (tableau) valide à utiliser)
        """
        DataToEncrypt_utf8 = DataToEncrypt.encode('utf-8')
        encrypted = libc.Encrypt(k, DataToEncrypt.encode('utf-8'), len(DataToEncrypt_utf8))
        return encrypted
    except TypeError:
        pass
    except Exception as e:
        pass



def ReleaseBuffer(buffer):
    try:       
        """
        Il faut toujours libérer le tampon  donné par la fonction Decrypt ou Encrypt
     
        Lorsque le tampon a fini d'être utilisé, il faut le libérer
        """
        libc.ReleaseBuffer(buffer)
    except TypeError:
        pass
    except Exception as e:
        pass
              
def ReleaseKey(k):
    try:       
        """
        Doit être utilisé pour libérer une instance MD159
	    lorsqu'elle n'est plus nécessaire.
     
        Lorsque la clé a fini d'être utilisé, il faut la libérer
        """
        libc.ReleaseInst(k)
    except TypeError:
        pass
    except Exception as e:
        print(e)

def Nty_decryptor(k,filename,extension,):
    with open(f"./{filename}", "rb") as file:
        encrypted = file.read()
    encryptedLength = len(encrypted)

    decrypted = ctypes.c_char_p(None)  # Initialisation d'un pointeur nul
    decryptedLength = libc.DecryptNTY(k, encrypted, encryptedLength, ctypes.byref(decrypted), True)
    # Création du nouveau fichier PNG avec les données déchiffrées
    if extension == None:
        name = f"{filename}"
    else:
        name = f"{filename}{extension}"
    output_file_path = f"./{name}"
    with open(output_file_path, "wb") as output_file:
        output_file.write(ctypes.string_at(decrypted, decryptedLength))
    return name
