import json

class Plant:
    """
    Plant model
    """
    def __init__(
        self,
        id,
        name,
        description,
        image,
        invasiveness
    ):
        self.id = id
        self.name = name
        self.description = description
        self.image = image
        self.invasiveness = invasiveness

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "invasiveness": self.invasiveness
        }

    @staticmethod
    def from_dict(data):
        return Plant(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            image=data["image"],
            invasiveness=data["invasiveness"]
        )