"""Modelo de recursos do grupo."""

from pydantic import BaseModel


class Resources(BaseModel):
    """Quantidade de cada recurso.

    Attributes:
        food: Comida.
        water: Agua.
        wood: Madeira, usada em barricadas.
        scrap: Sucata.
        medicine: Remedios.
        ammo: Municao, usada pelos guardas.
    """

    food: int = 0
    water: int = 0
    wood: int = 0
    scrap: int = 0
    medicine: int = 0
    ammo: int = 0

    def covers(self, cost: "Resources") -> bool:
        """Indica se os recursos bastam para pagar um custo.

        Args:
            cost: Custo a pagar.

        Returns:
            True se todos os recursos forem maiores ou iguais ao custo.
        """
        return all(
            getattr(self, name) >= value for name, value in cost.model_dump().items()
        )

    def add(self, other: "Resources") -> None:
        """Soma outro conjunto de recursos a este.

        Args:
            other: Recursos a somar.
        """
        for name, value in other.model_dump().items():
            setattr(self, name, getattr(self, name) + value)

    def subtract(self, other: "Resources") -> None:
        """Subtrai outro conjunto de recursos, sem passar de zero.

        Args:
            other: Recursos a subtrair.
        """
        for name, value in other.model_dump().items():
            setattr(self, name, max(0, getattr(self, name) - value))

    def is_empty(self) -> bool:
        """Indica se nao ha nenhum recurso.

        Returns:
            True se todas as quantidades forem zero.
        """
        return not any(self.model_dump().values())

    def describe(self) -> str:
        """Resume os recursos nao nulos em texto.

        Returns:
            Texto como "food 3, wood 2", ou "nothing" se vazio.
        """
        parts = [f"{name} {value}" for name, value in self.model_dump().items() if value]
        return ", ".join(parts) if parts else "nothing"
