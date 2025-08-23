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
    
    def get_average_response_time(self):
        query = """
            select round(avg(response_time), 6) as avg_response_time from survey_results where active = 1;
        """
        
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    
    
    def list_survey_results(self):
        
        avg_response_time = self.get_average_response_time()
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
