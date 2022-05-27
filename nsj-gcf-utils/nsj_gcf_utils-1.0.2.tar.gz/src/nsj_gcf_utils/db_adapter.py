# import sqlalchemy
import uuid


class DBAdapter:

    # TODO Refatorar para uso de parâmetros nomeados

    def __init__(self, db_connection):
        self._db = db_connection
        self._transaction = None

    def begin(self):
        if self._transaction is None:
            self._transaction = self._db.begin()

    def commit(self):
        if self._transaction is not None:
            self._transaction.commit()
            self._transaction = None

    def rollback(self):
        if self._transaction is not None:
            self._transaction.rollback()
            self._transaction = None

    def in_transaction(self):
        return self._transaction is not None

    def execute(self, sql: str, parameters=None) -> int:
        """
        Executando uma instrução sql sem retorno.
        É obrigatório a passagem de uma conexão de banco no argumento self._db.

        Retorna o número de linhas afetadas pela instrução.
        """
        cur = None
        try:
            cur = self._execute(sql, parameters)

            return cur.rowcount
        finally:
            if cur is not None:
                cur.close()

    def execute_query_to_model(self, sql: str, model_class: object, parameters=None) -> list:
        """
        Executando uma instrução sql com retorno.
        O retorno é feito em forma de uma lista (list), com elementos do tipo passado pelo parâmetro
        "model_class".
        É importante destacar que para cada coluna do retorno, será procurado um atributo no model_class
        com mesmo nome, para setar o valor. Se este não for encontrado, a coluna do retorno é ignorada.
        """

        result = []
        cur = None
        try:
            cur = self._execute(sql, parameters)
            rs = cur.fetchall()

            for rec in rs:
                model = model_class()

                i = 0
                for column in cur.keys():
                    if (hasattr(model, column)):
                        setattr(model, column, rec[i])

                    i += 1

                result.append(model)

        finally:
            if cur is not None:
                cur.close()

        return result

    def execute_query(self, sql: str, parameters=None) -> list:
        """
        Executando uma instrução sql com retorno.
        O retorno é feito em forma de uma lista (list), com elementos do tipo dict (onde cada chave é igual ao
        nome do campo correspondente).
        """
        cur = None
        try:
            cur = self._execute(sql, parameters)
            rs = cur.fetchall()

            return [dict(rec.items()) for rec in rs]
        finally:
            if cur is not None:
                cur.close()

    def execute_query_first_result(self, sql: str, model_class: object, parameters=None) -> "model_class":
        """
        Executando uma instrução sql com retorno.
        O retorno é feito em forma de um objeto do tipo passado pelo parâmetro "model_class".
        É importante destacar que para cada coluna do retorno, será procurado um atributo no model_class
        com mesmo nome, para setar o valor. Se este não for encontrado, a coluna do retorno é ignorada.
        """

        result = None
        cur = None
        try:
            cur = self._execute(sql, parameters)
            rs = cur.fetchone()

            if (len(rs) > 0):
                model = model_class()

                i = 0
                for column in cur.keys():
                    if (hasattr(model, column)):
                        setattr(model, column, rs[i])

                    i += 1

                result = model

        finally:
            if cur is not None:
                cur.close()

        return result

    def get_single_result(self, sql: str, parameters=None):
        """
        Executa uma instrução SQL para a qual se espera um único retorno (com tipo primitivo). Exemplo:
        select 1+1
        Se não houver retorno, retorna None.
        """
        cur = None
        try:
            cur = self._execute(sql, parameters)
            return cur.scalar()
        finally:
            if cur is not None:
                cur.close()

    def _check_type(self, parameter):
        if (isinstance(parameter, uuid.UUID)):
            return str(parameter)
        else:
            return parameter

    def _execute(self, sql: str, parameters: list):
        new_transaction = not self.in_transaction()

        try:
            if new_transaction:
                self.begin()

            if (parameters != None):
                pars = [self._check_type(par) for par in parameters]
                return self._db.execute(sql, pars)
            else:
                return self._db.execute(sql)
        except:
            if new_transaction:
                self.rollback()
            raise
        finally:
            if new_transaction:
                self.commit()

    def execute_query_from_file(self, query_file_path, *parameters):
        with open(query_file_path) as f:
            sql = f.read()
        return self.execute_query(sql, parameters)


# class AlchemyDBAdapter:
#     def __init__(self, db_connection):
#         self._db = db_connection

#     def execute_query(self, sql: str, **kwargs) -> list:
#         """
#         Executando uma instrução sql com retorno.
#         O retorno é feito em forma de uma lista (list), com elementos do tipo dict (onde cada chave é igual ao
#         nome do campo correspondente).
#         """
#         cur = None
#         sql = sqlalchemy.text(sql)
#         try:
#             cur = self._db.execute(sql, **kwargs)
#             rs = cur.fetchall()

#             return [dict(rec.items()) for rec in rs]
#         finally:
#             if cur is not None:
#                 cur.close()

#     def execute(self, sql: str, **kwargs) -> int:
#         """
#         Executando uma instrução sql sem retorno.
#         É obrigatório a passagem de uma conexão de banco no argumento self._db.

#         Retorna o número de linhas afetadas pela instrução.
#         """
#         cur = None
#         sql = sqlalchemy.text(sql)
#         try:
#             with self._db.begin():
#                 cur = self._db.execute(sql, **kwargs)

#             return cur.rowcount
#         finally:
#             if cur is not None:
#                 cur.close()

#     def execute_query_from_file(self, query_file_path, **kwargs):
#         with open(query_file_path) as f:
#             sql = f.read()
#         return self.execute_query(sql, **kwargs)

#     def execute_from_file(self, sql_file_path, **kwargs):
#         with open(sql_file_path) as f:
#             sql = f.read()
#         return self.execute(sql, **kwargs)
