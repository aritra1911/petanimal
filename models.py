from typing import Tuple, Any

class Pet:
    def __init__(self, id: int, category: str, breed: str, price: float,
                       owner: str) -> None:
        self.id = id
        self.category = category
        self.breed = breed
        self.price = price
        self.owner = owner

    def get_details(self) -> Tuple[int, str, str, float, str]:
        return (self.id, self.category, self.breed, self.price, self.owner)

    def get_id(self) -> int:
        return self.id

    def get_category(self) -> str:
        return self.category.capitalize()

    def get_breed(self) -> str:
        return self.breed

    def get_price(self) -> float:
        return self.price

    def get_owner(self) -> str:
        return self.owner