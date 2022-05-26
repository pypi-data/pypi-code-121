import ssl
from ldap3 import Connection, Server, ServerPool, SAFE_RESTARTABLE, Tls, AUTO_BIND_NONE
from perun.connector.utils.Logger import Logger
import time
import json


class LdapConnector:
    def __init__(self, config):
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._servers = ServerPool()
        for server in config['servers']:
            self._servers.add(Server(server['hostname'],
                                     tls=Tls(validate=ssl.CERT_NONE)))

        self._enableTLS = False
        if config['start_tls'] == 'true':
            self._enableTLS = True

        self._user = config['username']
        self._password = config['password']
        self._conn = Connection(server=self._servers, auto_bind=AUTO_BIND_NONE,
                                user=self._user, password=self._password,
                                version=3, client_strategy=SAFE_RESTARTABLE,
                                read_only=True)
        if not self._conn:
            raise Exception("Unable to connect to the Perun LDAP,")

        hostname = self._servers.get_current_server(self._conn)
        # enable TLS if required
        if self._enableTLS and not str(hostname).startswith("ldaps:"):
            if not self._conn.start_tls():
                raise Exception('Unable to force STARTTLS on Perun LDAP')

    def search_for_entity(self, base, filters,
                          attr_names=None):
        entries = self._search(base, filters, attr_names)
        if not entries:
            self._logger.debug(f"ldap_connector.search_for_entity "
                               f"- No entity found. Returning \'None\'. "
                               f"query base: {base} "
                               f", filter: {filters} ")
            return None

        if len(entries) > 1:
            raise Exception(f"ldap_connector.search_for_entity - "
                            f"More than one entity found. query base:"
                            f"{base}, filter: {filters}. Hint: Use "
                            f"method search_for_entities if you expect "
                            f"array of entities.")

        return entries[0]

    def search_for_entities(self, base, filters,
                            attr_names=None):
        entries = self._search(base, filters, attr_names)

        if not entries:
            self._logger.debug(f"ldap_connector.search_for_entities - "
                               f"No entities found. Returning empty "
                               f"array. query base: {base} "
                               f"filter: {filters} ")

            return entries

        return entries

    def _search(self, base, filters, attributes=None):
        hostname = self._servers.get_current_server(self._conn)
        if not self._conn.bind():
            raise Exception('Unable to bind user to the Perun LDAP,' +
                            hostname)
        self._logger.debug(f"ldap_connector.search - Connection "
                           f"to Perun LDAP established. Ready to "
                           f"perform search query. host: "
                           f"{hostname}, user: {self._user}")

        start_time = time.time()
        status, result, response, _ = \
            self._conn.search(search_base=base, search_filter=filters,
                              attributes=attributes)
        end_time = time.time()

        response_time = round(end_time - start_time, 3)
        if not response:
            return []

        entries = self._get_simplified_entries(response)

        self._conn.unbind()

        self._logger.debug(f"ldap_connector.search - search query "
                           f"proceeded in {str(response_time)}"
                           f"ms. Query base: {base}, filter: "
                           f"{filters}, response: ' "
                           f"{json.dumps(str(entries))}")

        return entries

    @staticmethod
    def _get_simplified_entries(result):

        entries = []
        for entry in result:
            entries.append(entry['attributes'])

        return entries
