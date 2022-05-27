
class PhotosSku:
    def __init__(self, base64_foto: str, codigo_erp_sku: str, codigo_foto: str, ordem: int, foto_padrao: bool):
        self.base64_foto: str = base64_foto
        self.codigo_erp_sku: str = codigo_erp_sku
        self.codigo_foto: str = codigo_foto
        self.ordem: str = ordem
        self.foto_padrao: bool = foto_padrao