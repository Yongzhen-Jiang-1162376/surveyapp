import json

class Configuration:
    """
    Configuration model
    """
    def __init__(
        self,
        id,
        number_of_image_pairs
    ):
        self.id = id
        self.number_of_image_pairs = number_of_image_pairs

    def to_dict(self):
        return {
            "id": self.id,
            "number_of_image_pairs": self.number_of_image_pairs
        }

    @staticmethod
    def from_dict(data):
        return Configuration(
            id=data["id"],
            name=data["number_of_image_pairs"]
        )
