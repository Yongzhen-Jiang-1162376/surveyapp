from project693.dao.base_dao import BaseDAO
from project693.model.configuration import Configuration
from typing import List
import json


class ConfigurationDAO(BaseDAO):
    """
    Data access object to get and update configuration
    """
    def __init__(self) -> None:
        super().__init__()

    # update configuration
    def update_configurtion(self, number_of_image_pairs: int) -> None:
        query = """
            UPDATE configuration
            SET number_of_image_pairs = %s
            WHERE id = 1;
        """
        self.execute_non_query(query, (number_of_image_pairs,))

    # get configuration
    def get_configuration(self) -> Configuration:
        query = """
            SELECT id, number_of_image_pairs
            FROM configuration
            WHERE id = 1;
        """
        result = self.execute_query(query)
        
        configuration = Configuration(
            id=result[0][0],
            number_of_image_pairs=result[0][1]
        )
        
        return configuration
