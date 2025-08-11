from project693.dao.base_dao import BaseDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer


class SurveyDAO(BaseDAO):
    def __init__(self) -> None:
        super().__init__()


    def save_metadata(self, metadata: SurveyMetadata):
        """
        Stores the introductory metadata: garden status, age range, and initial reasoning.
        """
        query = """
            INSERT INTO survey_metadata (session_id, has_garden, age, reasoning)
            VALUES (%s, %s, %s, %s)
        """
        self.execute_non_query(
            query,
            (
                metadata.session_id,
                metadata.has_garden,
                metadata.age,
                metadata.reasoning
            )
        )


    def update_reasoning(self, session_id: str, reasoning: str):
        """
        Updates the reasoning after Q10 is answered.
        """
        query = """
            UPDATE survey_metadata SET reasoning = %s WHERE session_id = %s
        """
        self.execute_non_query(query, (reasoning, session_id))


    def survey_answer(self, answer: SurveyAnswer):
        """
        Stores an answer to a survey question.
        """
        query = """
            INSERT INTO survey_results (session_id, question_seq, selected_plant_id)
            VALUES (%s, %s, %s)
        """
        self.execute_non_query(
            query,
            (
                answer.session_id,
                answer.question_number,
                answer.selected_plant_id
            )
        )