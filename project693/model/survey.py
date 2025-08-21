class SurveyMetadata:
    def __init__(self, session_id, has_garden=None, age=None, reasoning=None):
        self.session_id = session_id
        self.has_garden = has_garden
        self.age = age
        self.reasoning = reasoning

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "has_garden": self.has_garden,
            "age": self.age,
            "reasoning": self.reasoning
        }

    @staticmethod
    def from_dict(data):
        return SurveyMetadata(
            session_id=data["session_id"],
            has_garden=data.get("has_garden"),
            age=data.get("age"),
            reasoning=data.get("reasoning")
        )


class SurveyAnswer:
    def __init__(self, session_id, question_number, selected_plant_id, image_1_id, image_2_id, response_time):
        self.session_id = session_id
        self.question_number = question_number
        self.selected_plant_id = selected_plant_id
        self.image_1_id = image_1_id
        self.image_2_id = image_2_id
        self.response_time = response_time

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "question_number": self.question_number,
            "selected_plant_id": self.selected_plant_id,
            "image_1_id": self.image_1_id,
            "image_2_id": self.image_2_id,
            "response_time": self.response_time
        }

    @staticmethod
    def from_dict(data):
        return SurveyAnswer(
            session_id=data["session_id"],
            question_number=data["question_number"],
            selected_plant_id=data["selected_plant_id"],
            image_1_id=data["image_1_id"],
            image_2_id=data["image_2_id"],
            response_time=data["response_time"]
        )
