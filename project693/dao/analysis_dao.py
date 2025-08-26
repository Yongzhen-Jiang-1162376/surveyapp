from project693.dao.base_dao import BaseDAO


class AnalysisDAO(BaseDAO):
    def __init__(self) -> None:
        super().__init__()
    
    def list_survey_plants(self):
        """
        list all plants which have been chosen for survey
        """
        
        query = """
            select
                p.id,
                p.name
            from plants p
            inner join
            (
                select distinct invasive_plant_id as plant_id from survey_results where active = 1
                union
                select distinct non_invasive_plant_id as plant_id from survey_results where active = 1
            ) sr
            on p.id = sr.plant_id
            order by p.id;
        """
        
        result = self.execute_query(query)
        
        return result if result else []
    
    def get_current_average_response_time(self):
        query = """
            select round(avg(response_time), 6) as avg_response_time from survey_results where active = 1;
        """
        
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def get_current_total_survey_results(self):
        query = """
            select
                count(1) as total
            from survey_results sr
            where sr.active = 1    
        """
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    
    def list_survey_results(self):
        
        avg_response_time = self.get_current_average_response_time()
        # print('average response time')
        # print(avg_response_time)
        
        # if the response time is null, then set it as the average response time
        # Theoretically speaking, null response time is very much unlikely 
        # because the timing is only recorded after user submits
        query = """
            select
                sr.winner,
                sr.loser,
                ifnull(sr.response_time, %s) as response_time,
                sr.invasive_winner,
                sr.invasive_loser
            from survey_results sr
            where sr.active = 1
            order by sr.id;
        """
        
        result = self.execute_query(query, (avg_response_time,))
        
        return result if result else []


    def list_choice_count(self):
        query = """
            select
                sum(invasive_winner = 1) as invasive_count,
                sum(invasive_winner = 0) as non_invasive_count
            from survey_results
            where active = 1;
        """
        
        result = self.execute_query(query)
        
        return result if result else []

    def list_survey_age_group_count(self):
        # query = """
        #     select 
        #         sum(age='18-29') as '18-29',
        #         sum(age='30-49') as '30-49',
        #         sum(age='50-64') as '50-64',
        #         sum(age='65+') as '65+'
        #     from survey_metadata
        #     where session_id in
        #     (
        #         select distinct session_id from survey_results
        #     );
        # """
        
        query = """

            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where age = '18-29'
            )
            and active = 1
            
            union all
            
            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where age = '30-49'
            )
            and active = 1
            
            union all
            
            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where age = '50-64'
            )
            and active = 1
            
            union all
            
            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where age = '65+'
            )
            and active = 1
        """

        result = self.execute_query(query)

        return result if result else []
    
    def list_survey_gardening_count(self):
        query = """
            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where has_garden = 1
            )
            and active = 1

            union all

            select
                ifnull(sum(invasive_winner=1), 0) as invasive,
                ifnull(sum(invasive_winner=0), 0) as non_invasive
            from survey_results
            where session_id in
            (
                select session_id from survey_metadata where has_garden = 0
            )
            and active = 1
        """
        
        result = self.execute_query(query)
        
        return result if result else []

    def list_current_survey_results_with_plant_name(self):
        avg_response_time = self.get_current_average_response_time()
        
        query = """
            select
                sr.session_id,
                sr.question_seq,
                date_format(sr.submission_time, '%m-%d-%Y %H:%i:%S') as submission_time,
                ifnull(sr.response_time, %s) as response_time,
                sr.invasive_plant_id,
                p.name as invasive_plant_name,
                sr.non_invasive_plant_id,
                p1.name as non_invasive_plant_name,
                sr.selected_plant_id,
                p2.name as selected_plant_name,
                if(sm.has_garden = 1, 'Yes', 'No') as has_garden,
                sm.age as age_group,
                sm.reasoning as reasoning,
                sr.invasive_winner as invasive_win
            from survey_results sr
            inner join plants p on sr.invasive_plant_id = p.id
            inner join plants p1 on sr.non_invasive_plant_id = p1.id
            inner join plants p2 on sr.selected_plant_id = p2.id
            left join survey_metadata sm on sr.session_id = sm.session_id
            where sr.active = 1
            order by sr.submission_time, sr.question_seq;
        """

        result = self.execute_query(query, (avg_response_time,))        
        return result if result else []


    def list_current_survey_results_with_plant_name_paginated(self, limit, offset):
        avg_response_time = self.get_current_average_response_time()
        
        query = """
            select
                sr.session_id,
                sr.question_seq,
                date_format(sr.submission_time, '%m-%d-%Y %H:%i:%S') as submission_time,
                ifnull(round(sr.response_time, 5), %s) as response_time,
                sr.invasive_plant_id,
                p.name as invasive_plant_name,
                sr.non_invasive_plant_id,
                p1.name as non_invasive_plant_name,
                sr.selected_plant_id,
                p2.name as selected_plant_name,
                if(sm.has_garden = 1, 'Yes', 'No') as has_garden,
                sm.age as age_group,
                sm.reasoning as reasoning,
                sr.invasive_winner as invasive_win
            from survey_results sr
            inner join plants p on sr.invasive_plant_id = p.id
            inner join plants p1 on sr.non_invasive_plant_id = p1.id
            inner join plants p2 on sr.selected_plant_id = p2.id
            left join survey_metadata sm on sr.session_id = sm.session_id
            where sr.active = 1
            order by sr.submission_time, sr.question_seq
            limit %s offset %s;
        """

        result = self.execute_query(query, (avg_response_time, limit, offset))        
        return result if result else []
    
    
    def list_all_current_survey_results_with_plant_name(self):
        avg_response_time = self.get_current_average_response_time()
        
        query = """
            select
                sr.session_id,
                sr.question_seq,
                date_format(sr.submission_time, '%m-%d-%Y %H:%i:%S') as submission_time,
                ifnull(round(sr.response_time, 5), %s) as response_time,
                sr.invasive_plant_id,
                p.name as invasive_plant_name,
                sr.non_invasive_plant_id,
                p1.name as non_invasive_plant_name,
                sr.selected_plant_id,
                p2.name as selected_plant_name,
                if(sm.has_garden = 1, 'Yes', 'No') as has_garden,
                sm.age as age_group,
                sm.reasoning as reasoning,
                sr.invasive_winner as invasive_win
            from survey_results sr
            inner join plants p on sr.invasive_plant_id = p.id
            inner join plants p1 on sr.non_invasive_plant_id = p1.id
            inner join plants p2 on sr.selected_plant_id = p2.id
            left join survey_metadata sm on sr.session_id = sm.session_id
            where sr.active = 1
            order by sr.submission_time, sr.question_seq;
        """

        result = self.execute_query(query, (avg_response_time,))        
        return result if result else []
