from project693.dao.base_dao import BaseDAO
from project693.model.plant import Plant
from typing import List
import json
import random # this is for project693


class PlantDAO(BaseDAO):
    """
    Data access object for plants
    """
    def __init__(self) -> None:
        super().__init__()

    # add plant function
    def add_plant(self, name: str, description: str, image: str, invasiveness: str) -> None:
        query = """
            INSERT INTO plants (name, description, image, invasiveness, created_at, updated_at)
            VALUES (%s, %s, %s, %s, now(), now());
        """
        self.execute_non_query(query, (name, description, image, invasiveness))

    # edit plant function
    def edit_plant(self, id: int, name: str, invasiveness: str, description: str, image: str) -> None:
        query = """
            UPDATE plants
            SET name = %s, description = %s, invasiveness = %s, image = %s, updated_at = now()
            WHERE id = %s;
        """
        self.execute_non_query(query, (name, description, invasiveness, image, id))
    
    # update plant AI-generated description
    def update_plant_ai_description(self, id: int, ai_description: str) -> None:
        query = """
            update plants
                set ai_intro = %s
            where id = %s;
        """
        self.execute_non_query(query, (ai_description, id))

    # delete plant function
    def delete_plant(self, id: int) -> None:
        query = "DELETE FROM plants WHERE id = %s"
        self.execute_non_query(query, (id,))

    # search plant
    def search_plants(self, keyword: str) -> List[Plant]:
        query = """
            SELECT id, name, description, image, invasiveness
            FROM plants
            WHERE name LIKE %s OR description LIKE %s
            order by updated_at desc, id desc;
        """
        result = self.execute_query(query, (f"%{keyword}%", f"%{keyword}%"))
        
        plants = []
        for row in result:
            plant = Plant(
                id=row[0], 
                name=row[1], 
                description=row[2], 
                image=row[3],
                invasiveness=row[4]
            )
            plants.append(plant)
        
        return plants

    # get plant by plant id
    def get_plant_by_id(self, id: int) -> Plant:
        query = "SELECT * FROM plants WHERE id = %s"
        result = self.execute_query(query, (id,))
        if result:
            row = result[0]
            return Plant(
                id=row[0],
                name=row[1],
                description=row[2],
                image=row[3],
                invasiveness=row[4]
            )
        return None
    
    # get AI-generated description by plant id
    def get_ai_intro_by_id(self, id: int) -> str:
        query = """
            select
                ai_intro
            from plants
            where id = %s;
        """
        result = self.execute_query(query, (id,))
        return result[0][0] if result else None
    
    # get all plant information
    def get_all_plants(self) -> List[Plant]:
        query = "SELECT id, name, description, image, invasiveness FROM plants"
        result = self.execute_query(query)

        plants = []
        for row in result:
            plant = Plant(
                id=row[0],
                name=row[1],
                description=row[2],
                image=row[3],
                invasiveness=row[4]
            )
            plants.append(plant)
        
        return plants
    
    # get random pair of plants for survey
    def get_random_pair(self, used_invasive_ids=None, used_non_invasive_ids=None) -> List[Plant]:
        all_plants = self.get_all_plants()

        # Separate the plants
        invasive = [c for c in all_plants if c.invasiveness == 'invasive']
        non_invasive = [c for c in all_plants if c.invasiveness == 'non-invasive']

        # Filter out already used plants
        if used_invasive_ids:
            invasive = [c for c in invasive if c.id not in used_invasive_ids]
        if used_non_invasive_ids:
            non_invasive = [c for c in non_invasive if c.id not in used_non_invasive_ids]

        # If none left, return empty
        if not invasive or not non_invasive:
            return []

        # Pick one of each and shuffle
        return random.sample([
            random.choice(invasive),
            random.choice(non_invasive)
        ], 2)
