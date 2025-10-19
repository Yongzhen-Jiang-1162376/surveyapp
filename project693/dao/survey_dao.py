from project693.dao.base_dao import BaseDAO
from project693.dao.plant_dao import PlantDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer


class SurveyDAO(BaseDAO):
    """
    Data access object for survey data
    """
    def __init__(self) -> None:
        super().__init__()

    # save meta data
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

    # update reasoning preference
    def update_reasoning(self, session_id: str, reasoning: str):
        """
        Updates the reasoning after Q10 is answered.
        """
        query = """
            UPDATE survey_metadata SET reasoning = %s WHERE session_id = %s
        """
        self.execute_non_query(query, (reasoning, session_id))

    # save survey choice made by user
    def survey_answer(self, answer: SurveyAnswer):
        """
        Stores an answer to a survey question.
        """
        
        cycle_id = self.get_active_survey_cycle_id()
        
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
    
    # check whether an active survey cycle existed
    def active_survey_cycle_existed(self):
        """
        check whether an active survey cycle is existed
        """
        query = """
            select count(1) as count from survey_cycle where active = 1;
        """
        
        result = self.execute_query(query)
        return result
    
    # get current active survey cycle id
    def get_active_survey_cycle_id(self):
        """
        get the active (current) survey cycle id
        """
        query = """
            select id from survey_cycle where active = 1;
        """
        result = self.execute_query(query)
        return result[0][0]

    # check whether active survey result is existed
    def active_survey_result_existed(self):
        """
        check whether active survey result existed
        """
        query = """
            select count(1) from survey_results where active = 1;
        """
        result = self.execute_query(query)
        return result[0][0]
    
    # start a new survey cycle    
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

    # get all survey cycles
    def get_total_survey_cycles(self):
        query = """
            select count(1) from survey_cycle;  
        """
        result = self.execute_query(query)
        return result[0][0] if result else 0

    # get survey cycle data with pagination
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
    
    # get summary information for all surveys
    def list_all_survey_summary(self):
        
        query = """
        select
            count(distinct session_id) as survey_participants,
            count(1) as total_choices
        from survey_results;
        """

        result = self.execute_query(query)        
        return result if result else []

    # get survey summary for one session
    def list_survey_summary(self, session_id):
        query = """
            select
                p.name,
                p.invasiveness,
                p.id
            from survey_results sr
            inner join plants p on sr.selected_plant_id = p.id
            where sr.session_id = %s
            order by sr.question_seq;
        """
        
        result = self.execute_query(query, (session_id,))
        return result if result else []

    # get survery aggregation information for one survey session
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

    # get all survey cycle detailed record by cycle id
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
    
    # get single survey record by record id
    def get_survey_choice_detail_by_id(self, id):
        query = """
            select
                session_id,
                cycle_id
            from survey_results
            where id = %s;
        """
        result = self.execute_query(query, (id,))
        return result[0]
    
    # get choice id by session id
    # to check whether all records are deleted for this session
    def get_survey_choice_detail_by_session_id(self, session_id):
        query = """
            select
                id
            from survey_results
            where session_id = %s;
        """
        result = self.execute_query(query, (session_id,))
        return result if result else []
    
    # get choice id by cycle id
    # to check whether all choices are deleted for this cycle id
    def get_survey_choice_detail_by_cycle_id(self, cycle_id):
        query = """
            select
                id
            from survey_results
            where cycle_id = %s;
        """
        result = self.execute_query(query, (cycle_id,))
        return result if result else []
    
    # delete survey meta data by session id
    def delete_survey_meta_by_session_id(self, session_id):
        query = """
            delete from survey_metadata where session_id = %s;
        """
        self.execute_non_query(query, (session_id,))
    
    # check whether a cycle id is an active cycle
    def cycle_id_is_active(self, cycle_id):
        query = """
            select id from survey_cycle where id = %s and active = 1;
        """
        result = self.execute_query(query, (cycle_id,))
        return True if result else False
    
    # delete the whole cycle by cycle id
    # def delete_survey_cycle_by_id(self, cycle_id):
    #     query = """
    #         delete from survey_cycle where id = %s;
    #     """
    #     self.execute_non_query(query, (cycle_id,))
    
    # delete beat score by invasive by by cycle id    
    def delete_beta_score_by_invasive_type_hist_by_cycle_id(self, cycle_id):
        query = """
            delete from bt_beta_score_by_invasive_type_histogram where cycle_id = %s;
        """
        self.execute_non_query(query, (cycle_id,))
    
    # delete beta score for heat map by cycle id
    def delete_beta_score_heat_map_by_cycle_id(self, cycle_id):
        query = """
            delete from bt_beta_score_heat_map where cycle_id = %s;
        """
        self.execute_non_query(query, (cycle_id,))
    
    # delete beta score vs win percentage by cycle id
    def delete_beta_score_win_percentage_by_cycle_id(self, cycle_id):
        query = """
            delete from bt_beta_score_win_percentage where cycle_id = %s;
        """
        self.execute_non_query(query, (cycle_id,))
    
    # delete win/loss by plant by cycle id
    def delete_win_loss_by_plant_by_cycle_id(self, cycle_id):
        query = """
            delete from win_loss_by_plant where cycle_id = %s;
        """
        self.execute_non_query(query, (cycle_id,))
        
    # delete survey choice by record id
    def delete_survey_choice_by_id(self, id):
        
        session_id, cycle_id = self.get_survey_choice_detail_by_id(id)
        
        query = """
            delete from survey_results where id = %s;
        """
        self.execute_non_query(query, (id,))
        
        # if all choices in that session has been deleted, then delete the metadata
        meta_data_res = self.get_survey_choice_detail_by_session_id(session_id)
        if not meta_data_res:
            self.delete_survey_meta_by_session_id(session_id)
        
        # if all survey choices are deleted in the cycle, and the cycle is not
        # the active one, then delete the cycle as well
        cycle_data_res = self.get_survey_choice_detail_by_cycle_id(cycle_id)
        if not cycle_data_res and not self.cycle_id_is_active(cycle_id):
            self.delete_beta_score_heat_map_by_cycle_id(cycle_id)
            self.delete_beta_score_by_invasive_type_hist_by_cycle_id(cycle_id)
            self.delete_beta_score_win_percentage_by_cycle_id(cycle_id)
            self.delete_win_loss_by_plant_by_cycle_id(cycle_id)
            
            self.delete_survey_cycle_by_id(cycle_id)

    # delete survey cycle by id
    def delete_survey_cycle_by_id(self, cycle_id):
        
        query = """
            select 
                distinct session_id
            from survey_results
            where cycle_id = %s
        """
        session_ids = self.execute_query(query, (cycle_id,))
        
        print('-----------------------1-----------------------')
        print(session_ids)
        
        # convert to a list
        session_ids = [s[0] for s in session_ids]
        
        if session_ids:
            # delete survey results
            query = """
                delete from survey_results where cycle_id = %s;
            """
            self.execute_non_query(query, (cycle_id,))
        
            # delete survey metadata
            placeholders = ', '.join(['%s'] * len(session_ids))
            print('-----------------------2-----------------------')
            print(placeholders)
            query = f"""
                delete from survey_metadata where session_id in ({placeholders})
            """
            self.execute_non_query(query, tuple(session_ids))
        
        # need to delete survey_results first because of foreign key
        
        
        # delete analysis data for this cycle
        self.delete_beta_score_heat_map_by_cycle_id(cycle_id)
        self.delete_beta_score_by_invasive_type_hist_by_cycle_id(cycle_id)
        self.delete_beta_score_win_percentage_by_cycle_id(cycle_id)
        self.delete_win_loss_by_plant_by_cycle_id(cycle_id)
        
        # if there's no survey data available, then need to delete the analysis data for all survey cycle_id =0
        result = self.survey_results_available()
        print('-----------------------3-----------------------')
        print(result)
        if not result:
            self.delete_beta_score_heat_map_by_cycle_id(0)
            self.delete_beta_score_by_invasive_type_hist_by_cycle_id(0)
            self.delete_beta_score_win_percentage_by_cycle_id(0)
            self.delete_win_loss_by_plant_by_cycle_id(0)
        
        # delete survey_cycle table only if the cycle is not active
        query = """
            delete from survey_cycle where id = %s and active != 1;
        """
        self.execute_non_query(query, (cycle_id,))
    
    def survey_results_available(self):
        query = """
            select count(1) as total from survey_results;
        """
        result = self.execute_query(query)
        print('------------------------- result ----------------------')
        print(result)
        return 1 if result[0][0] else 0

    # get survey preference summary data
    def get_survey_preference_summary(self):
        query = """
            SELECT
                if(count(1) = 0, 0, SUM(reasoning = 'Dominant Flower Colour') / count(1)) as r1_perc,
                SUM(reasoning = 'Dominant Flower Colour') AS r1_count,
                if(count(1) = 0, 0, SUM(reasoning = 'Contrasting Colours') / count(1)) as r2_perc,
                SUM(reasoning = 'Contrasting Colours') AS r2_count,
                if(count(1) = 0, 0, SUM(reasoning = 'Flower Shape') / count(1)) as r3_perc,
                SUM(reasoning = 'Flower Shape') AS r3_count,
                if(count(1) = 0, 0, SUM(reasoning = 'Familiarity') / count(1)) as r4_perc,
                SUM(reasoning = 'Familiarity') AS r4_count,
                if(count(1) = 0, 0, SUM(reasoning = 'Different From Most Plant You Know') / count(1)) as r5_perc,
                SUM(reasoning = 'Different From Most Plant You Know') AS r5_count,
                count(1) as total
            FROM survey_metadata
            where session_id in (select distinct session_id from survey_results);    
        """
        
        result = self.execute_query(query)
        return result[0]
    
    # get survey preference statistical data
    def get_survey_preference_statistics(self, pref):
        query = """
            select
                %s as preference,
                if(count(1) = 0, 0, sum(age = '18-29') / count(1)) as ag1_perc,
                ifnull(sum(age = '18-29'), 0) as age1,
                if(count(1) = 0, 0, sum(age = '30-49') / count(1)) as ag2_perc,
                ifnull(sum(age = '30-49'), 0) as age2,
                if(count(1) = 0, 0, sum(age = '50-64') / count(1)) as ag3_perc,
                ifnull(sum(age = '50-64'), 0) as age3,
                if(count(1) = 0, 0, sum(age = '65+') / count(1)) as ag4_perc,
                ifnull(sum(age = '65+'), 0) as age4,
                if(count(1) = 0, 0, sum(has_garden = 1) / count(1)) as gardener_perc,
                ifnull(sum(has_garden = 1), 0) as gardener,
                if(count(1) = 0, 0, sum(has_garden = 0) / count(1)) as non_gardener_perc,
                ifnull(sum(has_garden = 0), 0) as non_gardener,
                ifnull(count(1), 0) as total
            FROM survey_metadata
            where reasoning = %s
            and session_id in (select distinct session_id from survey_results);
        """
        result = self.execute_query(query, (pref, pref,))
        return result[0]

    # get all survey meta data count
    def get_all_survey_meta_data_count(self):
        query = """
            select
                count(1) as total
            from survey_metadata sm
            where session_id in (select distinct session_id from survey_results);
        """
        result = self.execute_query(query)
        return result[0][0] if result else 0

    # get all survey meta data paginated
    def list_all_survey_meta_data_paginated(self, limit, offset):
        query = """
            select
                session_id,
                date_format(sm.submitted_at, '%m-%d-%Y %H:%i:%S') as submission_time,
                has_garden,
                age as age_group,
                reasoning as preference
            from survey_metadata sm
            where session_id in (select distinct session_id from survey_results)
            order by submitted_at
            limit %s offset %s;
        """

        result = self.execute_query(query, (limit, offset))        
        return result if result else []
    
    # get all survey meta data
    def list_all_survey_meta_data(self):
        query = """
            select
                session_id,
                date_format(sm.submitted_at, '%m-%d-%Y %H:%i:%S') as submission_time,
                has_garden,
                age as age_group,
                reasoning as preference
            from survey_metadata sm
            where session_id in (select distinct session_id from survey_results)
            order by submitted_at;
        """

        result = self.execute_query(query)        
        return result if result else []
