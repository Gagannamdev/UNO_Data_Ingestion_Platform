from abc import ABC, abstractmethod


class BaseDatabaseAdapter(ABC):

    @abstractmethod
    async def test_connection(self) -> dict:
        pass

    @abstractmethod
    async def list_tables(self) -> list[str]:
        pass

    @abstractmethod
    async def preview_data(
        self,
        table_name: str,
        limit: int = 20,
    ) -> list[dict]:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass
