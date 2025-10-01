from project693.dao.base_dao import BaseDAO
from project693.dao.plant_dao import PlantDAO
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
        
        cycle_id = self.get_active_survey_cycle_id()
        print(cycle_id)
        
        plantDao = PlantDAO()
        plant = plantDao.get_plant_by_id(answer.selected_plant_id)
        
        if (plant.invasiveness == 'invasive'):
            invasive_plant_id, non_invasive_plant_id = (answer.image_1_id, answer.image_2_id) if (answer.selected_plant_id == answer.image_1_id) else (answer.image_2_id, answer.image_1_id)
        else:
            invasive_plant_id, non_invasive_plant_id = (answer.image_2_id, answer.image_1_id) if (answer.selected_plant_id == answer.image_1_id) else (answer.image_1_id, answer.image_2_id)
        
        winner = answer.selected_plant_id
        loser = answer.image_2_id if answer.selected_plant_id == answer.image_1_id else answer.image_1_id
        
        invasive_winner = 1 if (plant.invasiveness == 'invasive') else 0
        invasive_loser = 0 if (plant.invasiveness == 'invasive') else 1

        query = """
            INSERT INTO survey_results (
                session_id,
                question_seq,
                selected_plant_id,
                response_time,
                invasive_plant_id,
                non_invasive_plant_id,
                winner,
                loser,
                invasive_winner,
                invasive_loser,
                active,
                cycle_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.execute_non_query(
            query,
            (
                answer.session_id,
                answer.question_number,
                answer.selected_plant_id,
                answer.response_time,
                invasive_plant_id,
                non_invasive_plant_id,
                winner,
                loser,
                invasive_winner,
                invasive_loser,
                1,
                cycle_id
            )
        )
    
    def active_survey_cycle_existed(self):
        """
        check whether an active survey cycle is existed
        """
        query = """
            select count(1) as count from survey_cycle where active = 1;
        """
        
        result = self.execute_query(query)
        return result
    
    def get_active_survey_cycle_id(self):
        """
        get the active (current) survey cycle id
        """
        query = """
            select id from survey_cycle where active = 1;
        """
        result = self.execute_query(query)
        return result[0][0]

    def active_survey_result_existed(self):
        """
        check whether active survey result existed
        """
        query = """
            select count(1) from survey_results where active = 1;
        """
        result = self.execute_query(query)
        return result[0][0]
        
    def start_survey_cyle(self):
        """
        Start a new survey cycle
        """
        
        # make all existing survey cycle as active = 0
        query = """
            update survey_cycle set active = 0, end_time = now() where active = 1;
        """
        self.execute_non_query(query)
        
        query = """
            update survey_results set active = 0 where active = 1;
        """
        self.execute_non_query(query)
        
        query = """
            insert into survey_cycle (start_time, active) values (now(), 1);
        """
        self.execute_non_query(query)


    def get_total_survey_cycles(self):
        query = """
            select count(1) from survey_cycle;  
        """
        result = self.execute_query(query)
        return result[0][0] if result else 0


    def list_survey_cycle_paginated(self, limit, offset):
        
        query = """
            select 
                id as cycle_id, 
                date_format(start_time, '%d-%m-%Y %H:%i:%S') as start_time,
                date_format(end_time, '%d-%m-%Y %H:%i:%S') as end_time,
                m.survey_participants,
                m.total_choices, 
                if(active = 1, 'Active', 'Closed') as status
            from survey_cycle sc
            left join
            (
                select
                    cycle_id,
                    count(distinct session_id) as survey_participants,
                    count(1) as total_choices
                from survey_results
                group by cycle_id
            ) as m on sc.id = m.cycle_id
            order by id
            limit %s offset %s;
            ;
        """

        result = self.execute_query(query, (limit, offset))        
        return result if result else []


    def list_survey_summary(self, session_id):
        query = """
            select
                p.name,
                p.invasiveness
            from survey_results sr
            inner join plants p on sr.selected_plant_id = p.id
            where sr.session_id = %s
            order by sr.question_seq;
        """
        
        result = self.execute_query(query, (session_id,))
        return result if result else []


    def list_survey_summary_aggregation(self, session_id):
        query = """
            select
                sum(invasive_winner) as invasive_count,
                sum(invasive_loser) as non_invasive_count
            from survey_results
            where session_id = %s;
        """
        
        result = self.execute_query(query, (session_id,))
        return result[0]


    def list_survey_cycle_detail_data(self, cycle_id):
        query = """
            select
                sr.id,
                sr.session_id,
                sr.question_seq,
                date_format(sr.submission_time, '%m-%d-%Y %H:%i:%S') as submission_time,
                sr.response_time,
                sr.invasive_plant_id,
                p.name as invasive_plant_name,
                sr.non_invasive_plant_id,
                p1.name as non_invasive_plant_name,
                sr.selected_plant_id,
                p2.name as selected_plant_name,
                sr.invasive_winner as invasive_win
            from survey_results sr
            inner join plants p on sr.invasive_plant_id = p.id
            inner join plants p1 on sr.non_invasive_plant_id = p1.id
            inner join plants p2 on sr.selected_plant_id = p2.id
            where sr.cycle_id = %s
            order by sr.submission_time, sr.question_seq;
        """
        result = self.execute_query(query, (cycle_id,))
        return result if result else []
