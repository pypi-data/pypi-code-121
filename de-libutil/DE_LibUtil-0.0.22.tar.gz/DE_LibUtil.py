import hashlib
import datetime as dt
import rsa
from cryptography.fernet import Fernet
import pandas as pd
import string
from random import choice

KEYS_RSA = rsa.newkeys(512)

class LIB:
    def __init__(self):
        pass

    @staticmethod
    def token_get(word: str) -> str:
        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(word.encode())
        return token.decode()

    @staticmethod
    def findchar(string: str, substring: str, ocorrencia: int, inicio: int = 0, fim: int = None):
        if fim is None:
            fim = len(string)
        if substring is None:
            return None
        if string is None:
            return None
        if ocorrencia is None:
            ocorrencia = 1
        while True:
            pass

    @staticmethod
    def build_key(size: int = 24,
                  sep: str = "-",
                  word_length: int = 4,
                  lower_case: bool = True,
                  upper_case: bool = True,
                  digits: bool = True,
                  hex_digits: bool = False,
                  oct_digits: bool = False,
                  special_chars: bool = False,
                  printable_chars: bool = False,
                  control_chars: bool = False
                  ):
        index = 1
        key = ""
        literal = ""
        if lower_case:
            literal = literal + string.ascii_lowercase
        if upper_case:
            literal = literal + string.ascii_uppercase
        if digits:
            literal = literal + string.digits
        if hex_digits:
            literal = literal + string.hexdigits
        if oct_digits:
            literal = literal + string.octdigits
        if special_chars:
            literal = literal + string.punctuation
        if printable_chars:
            literal = literal + string.printable
        if control_chars:
            literal = literal + string.whitespace
        try:
            for i in range(size):
                letra = choice(literal)
                if index == word_length and i < size - 1:
                    key += letra + sep
                    index = 1
                else:
                    key += letra
                    index += 1
        except Exception as error:
            key = f"Impossivel gerar uma chave. Erro: {error}"
        return key

    @staticmethod
    def hash(word: str, pattern: str = "md5"):
        pattern_list = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
        h, msg, error = None, None, None
        try:
            #value = b'{word}'
            if pattern == pattern_list[0]:
                h = hashlib.md5()
            elif pattern == pattern_list[1]:
                h = hashlib.sha1()
            elif pattern == pattern_list[2]:
                h = hashlib.sha224()
            elif pattern == pattern_list[3]:
                h = hashlib.sha256()
            elif pattern == pattern_list[4]:
                h = hashlib.sha384()
            elif pattern == pattern_list[5]:
                h = hashlib.sha512()
            h.update({word.encode()})
            msg = h.hexdigest()
        except Exception as error:
            msg = f"""Erro ao tentar montar o HASH. Erro: {error}"""
        finally:
            return msg

    @staticmethod
    def rsa_encrypt(word: str):
        msg = None
        try:
            PUBLIC_KEY = KEYS_RSA[0]
            msg = rsa.encrypt(word.encode(), PUBLIC_KEY)
            print(type(msg))
        except Exception as error:
            msg = f"""Falha ao tentar encriptografar a palavra {word}. Erro: {error}"""
        finally:
            return msg

    @staticmethod
    def rsa_decrypt(word: str):
        msg = None
        try:
            PRIVATE_KEY = KEYS_RSA[1]
            msg = rsa.decrypt(word.encode(), PRIVATE_KEY).decode()
        except Exception as error:
            msg = f"""Falha ao tentar Descriptografar a palavra {word}. Erro: {error}"""
        finally:
            return msg

    @staticmethod
    def Date_to_DateAsLong(value):
        try:
            dataaslong = int(dt.datetime.timestamp(value) * 1e3)
            return dataaslong
        except Exception as error:
            msgerro = f"""Falha ao tentar transformar um DATA em um LONG: "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def DateAsLong_to_Date(value):
        try:
            date = dt.datetime.fromtimestamp(value / 1e3)
            return date
        except Exception as error:
            msgerro = f"""Falha ao tentar transformar um LONG em uma data: "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def TimeAsLong_to_Time(value: dt.timedelta):
        try:
            horas_total = round((value.days * 24) + int(value.seconds / 60 / 60), 2)
            minutos = round(((value.seconds / 60 / 60) - int((value.seconds / 60) / 60)) * 60, 2)
            seg = round(((minutos - int(minutos)) * 60), 2)
            hora = f"""{horas_total}:{int(minutos):02}:{int(round(seg)):02}"""
            return hora
        except Exception as error:
            msgerro = f"""Falha ao tentar converter um timedelta para um tempo (HH:mm:ss) "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def Time_to_TimeAsLong(value):
        try:
            td = value.split(":")
            h = round(int(td[0]) * 60 * 60 * 1000)
            m = round(int(td[1]) * 60 * 1000)
            s = round(int(td[2]) * 1000)
            tempo = h + m + s
            return tempo
        except Exception as error:
            msgerro = f"""Falha ao tentar converter um horario em LONG "{value}". {error}"""
            raise Exception(msgerro)

    @staticmethod
    def ifnull(var, val):
        if (var is None or var == 'None'):
            value = val
        else:
            value = var
        return value

    @staticmethod
    def iif(condicao: bool, value_true, value_false):
        if condicao:
            value = value_true
        else:
            value = value_false
        return value

    @staticmethod
    def Crud(sql: str = None, values: dict = None, conexao = None, commit: bool = True):
        msg, result, linhas_afetadas = None, [], 0
        try:
            if not isinstance(sql, str) or sql is None:
                raise Exception(f"""Comando sql não foi definido {sql}""")
            if conexao is None:
                raise Exception(f"""Conexão não foi informada {conexao}""")
            if not isinstance(values, dict):
                raise Exception(f"""Lista de valores não foi informada {values}""")
            cursor = conexao.cursor()
            cursor.execute(sql, values)
            linhas_afetadas = cursor.rowcount
            cursor.close()
            if commit:
                conexao.commit()
            msg = f"""Comando SQL executado com sucesso!"""
        except Exception as error:
            msg = f"""Falha ao tentar executar o comando SQL! Erro: {error}"""
            result = msg
        finally:
            result = {"linhas_afetadas": linhas_afetadas, "mensagem": msg, "sql": sql}
            return result

    @staticmethod
    def CRYPTOGRAPHY(word, action: str = "D", token: str = None):
        # D=Decrypt, E=Encrypt
        result = None
        try:
            if word is None:
                raise Exception(f"""Parametro "word" é obrigatorio!""")
            if token is None:
                raise Exception(f"""Parametro "token" é obrigatório""")
            if isinstance(word, str):
                word = word.encode()
            CIPHER = Fernet(token)
            if action == "E":
                if type(word == "str"):
                    result = CIPHER.encrypt(word)
            else:
                result = CIPHER.decrypt(word)
        except Exception as error:
            result = error
        finally:
            return result.decode()

    @staticmethod
    def get_parametros_geral(conexao) -> pd.DataFrame:
        df = None
        now = dt.datetime.now()
        status = 'A' # Ativo
        try:
            sql = f"""
                   SELECT *
                     FROM Parametros
                    where flg_status = 'A'
                      and to_date({now.astype(str)}, "%Y-%m-%d %H:%MM:%S") between dat_ini_vigencia and dat_fim_vigencia
                      and flg_status = '{status}'
                    order by handle_parent, handle, num_ordem
                   """
            df = pd.read_sql(con=conexao, sql=sql)
        except Exception as error:
            df = error
        finally:
            return df

    @staticmethod
    def get_parametro_valor(df, value) -> str:
        result = None
        try:
            index = df.loc[df["nom_variavel"] == value].index[0]
            result = df.loc[index, "val_parametro"]
        except Exception as error:
            result = None
        finally:
            return result

    @staticmethod
    def get_parametro_valor_index(df, value) -> int:
        result = None
        try:
            result = df.loc[df["nom_variavel"] == value].index[0]
        except Exception as error:
            result = None
        finally:
            return result

    @staticmethod
    def get_parametros_grupo(df, value) -> pd.DataFrame:
        result = None
        try:
            result = df.loc[df["grupo_parametro"] == value]
        except Exception as error:
            result = error
        finally:
            return result

    @staticmethod
    def get_parametros_familia(df, value) -> pd.DataFrame:
        result = None
        try:
            result = df.loc[df["familia"] == value]
        except Exception as error:
            result = error
        finally:
            return result
        
    @staticmethod
    def parametro_set(conexao, nom_parametro, val_parametro):
        result = None
        try:
            sql = f"""
                    Update Parametros
                       set val_parametro = '{val_parametro}'
                     where nom_variavel = = '{nom_parametro}'   
                  """
            cursor = conexao.cursor()
            cursor.execute(sql)
            conexao.commit()
            conexao.close()
        except Exception as error:
            msg = f"""Falha ao tentar gravar o parametro [{nom_parametro}, com o valor [{val_parametro}], nesta conexão [{conexao}]. Erro: {error}"""
            result = msg
            if conexao.isopen():
                conexao.close()
        finally:
            return result

    @staticmethod
    def cores_ansi() -> dict:
        cores = {"Preto": ["\033[1;30m", "\033[1;40m"],
                 "Vermelho": ["\033[1;31m", "\033[1;41m"],
                 "Verde": ["\033[1;32m", "\033[1;42m"],
                 "Amarelo": ["\033[1;33m", "\033[1;43m"],
                 "Azul": ["\033[1;34m", "\033[1;44m"],
                 "Magenta": ["\033[1;35m", "\033[1;45m"],
                 "Cyan": ["\033[1;36m", "\033[1;46m"],
                 "Cinza Claro": ["\033[1;37m", "\033[1;47m"],
                 "Cinza Escuro": ["\033[1;90m", "\033[1;100m"],
                 "Vermelho Claro": ["\033[1;91m", "\033[1;101m"],
                 "Verde Claro": ["\033[1;92m", "\033[1;102m"],
                 "Amarelo Claro": ["\033[1;93m", "\033[1;103m"],
                 "Azul Claro": ["\033[1;94m", "\033[1;104m"],
                 "Magenta Claro": ["\033[1;95m", "\033[1;105m"],
                 "Cyan Claro": ["\033[1;96m", "\033[1;106m"],
                 "Branco": ["\033[1;97m", "\033[1;107m"],
                 "Negrito": ["\033[;1m", None],
                 "Inverte": ["\033[;7m", None],
                 "Reset (remove formatação)": ["\033[0;0m", None]}
        return cores

if __name__ == "__main__":
    x = LIB()
    t = x.token_get("D@S@")
    print(t)

