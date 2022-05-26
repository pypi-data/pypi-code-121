import sys
import json
from oneparams.api.base_diff import BaseDiff


class ApiProdutos(BaseDiff):
    """
    Gerenciamento de serviços,
    cria, atualiza, deleta e inativa serviços
    """
    items: dict = {}
    list_details: dict = {}
    first_get = False

    def __init__(self):
        super().__init__(key_id="produtosId",
                         key_name="descricao",
                         item_name="product",
                         url_create=None,
                         url_update=None,
                         url_get_all="/OProdutos/ListaDetalhesProdutos",
                         url_get_detail="/OProdutos/DetalhesProdutos",
                         key_detail=None,
                         url_delete="/OProdutos/DeleteProduto",
                         url_inactive="/OProdutos/UpdateProdutos",
                         key_active="ativo",
                         handle_errors={
                             "API.OPRODUTOS.DELETE.REFERENCE":
                             "Cant delete product"
                         })

        if not ApiProdutos.first_get:
            self.get_all()
            ApiProdutos.first_get = True

    def get_all(self):
        items = super().get_all()
        ApiProdutos.items = {}
        for i in items:
            ApiProdutos.items[i[self.key_id]] = {
                self.key_id: i[self.key_id],
                self.key_active: [self.key_active],
                self.key_name: i[self.key_name]
            }

    def add_item(self, data: dict, response: dict) -> int:
        item_id = response["data"]
        data = {
            self.key_id: item_id,
            self.key_name: data[self.key_name],
            self.key_active: data[self.key_active]
        }
        self.items[item_id] = data
        return item_id

    def details(self, item_id: int) -> dict:
        try:
            return self.list_details[item_id]
        except KeyError:
            response = self.get(f"{self.url_get_detail}/{item_id}")
            self.status_ok(response)

            content = json.loads(response.content)
            content = content["produtosEProdutosPrecosTributosModel"]

            self.list_details[content["produtosLightModel"][
                self.key_id]] = content
            return content

        except AttributeError as exp:
            sys.exit(exp)

    def inactive(self, item_id: int) -> bool:
        """ Inativa um item cadastrado

        Retorna um valor boleano informando se o item
        foi inativado ou não
        """
        if self.url_inactive is None:
            return False

        data = self.details(item_id)
        key_active = data["produtosLightModel"][self.key_active]
        key_name = data["produtosLightModel"][self.key_name]
        key_id = data["produtosLightModel"][self.key_id]

        if not key_active:
            return True

        data["produtosLightModel"][self.key_active] = False

        print(
            f"inactivating {key_name} {self.item_name}"
        )
        response = self.put(
            f"{self.url_inactive}/{key_id}",
            data=data)

        if not self.status_ok(response):
            return False

        # atualizo o item na lista
        self.items[key_id][self.key_active] = False

        return True
