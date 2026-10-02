from Src.Models.organization_model import organization_model


class company_model(organization_model):
    """
    Модель карточки компании (совместимость с Patterns2026)
    """

    def __init__(
        self,
        name: str = "",
        inn: str = "",
        bik: str = "",
        account: str = "",
        ownership_form: str = "",
        corr_account: str = "",
    ):
        super().__init__(
            name=name,
            inn=inn,
            bik=bik,
            account=account,
            ownership_form=ownership_form,
        )
        if corr_account:
            self.corr_account = corr_account

    @property
    def bic(self) -> str:
        return self.bik

    @bic.setter
    def bic(self, value: str):
        self.bik = str(value)

    @property
    def ownership(self) -> str:
        return self.ownership_form

    @ownership.setter
    def ownership(self, value: str):
        self.ownership_form = str(value)

    @property
    def corr_account(self) -> str:
        return getattr(self, "_corr_account", "")

    @corr_account.setter
    def corr_account(self, value: str):
        self._corr_account = str(value).strip()
