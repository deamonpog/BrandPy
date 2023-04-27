from .bw_api_caller import BWAPICaller


class BWAPIHelper:
    BW_DATE_TIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%f%z"

    def __init__(self, in_bwapi_caller):
        """
        Initialize BWAPIHelper Object.
        :param in_bwapi_caller: The BWAPICaller object.
        :type in_bwapi_caller: BWAPICaller
        """
        self.bw_api_caller = in_bwapi_caller

    def get_projects(self):
        """
        Get all projects which are available for this user.
        Counts as 1 direct API call.
        :return: The JSON object returned from the API call.
        :rtype: JSON Object
        """
        url = "https://api.brandwatch.com/projects/summary"
        response = self.bw_api_caller.call_api(url, {})
        return response

    def get_queries(self, in_project_id):
        """
        Get all queries which are available for the given project.
        Counts as 1 direct API call.
        :return: The JSON object returned from the API call.
        :rtype: JSON Object
        """
        url = f"https://api.brandwatch.com/projects/{in_project_id}/queries/summary"
        response = self.bw_api_caller.call_api(url, {})
        return response

    def find_query_id_in_project(self, in_project_id, in_query_name):
        """
        Finds the ID of the query with the given query name in the given project if it exists. Otherwise, returns None.
        Internally calls self.get_queries once.
        :param in_project_id: ProjectID of the project
        :type in_project_id: int
        :param in_query_name: Name of the query.
        :type in_query_name: str
        :return: QueryID if it exists, otherwise None
        :rtype: Union[None, int]
        """
        all_queries = self.get_queries(in_project_id)
        for query in all_queries['results']:
            if query['name'] == in_query_name:
                return query['id']
        print("Query name : {} not found in the project {} ".format(in_query_name, in_project_id))
        return None

    def find_query_id(self, in_query_name):
        """
        Finds the IDs of the queries with the given query name in all available projects and return them as a dict.
        List would be empty if the query name is not found in any project.
        Internally calls self.get_projects and self.find_query_id_in_project.
        Number of calls made to the API is equal to the number of projects + 1.
        :param in_query_name: Name of the query.
        :type in_query_name: str
        :return: A list of (ProjectID, QueryID) pairs
        :rtype: list
        """
        project_to_query = []
        all_projects = self.get_projects()
        for project in all_projects['results']:
            query_id = self.find_query_id_in_project(project['id'], in_query_name)
            if query_id is not None:
                print("Query name found in project : {}".format(project['name']))
                project_to_query.append((project['id'], query_id, project['name']))
        return project_to_query

    @staticmethod
    def datetime_to_str(in_datetime):
        """
        Converts given datetime objects to string time representations that Brandwatch uses. ( strftime format : "%Y-%m-%dT%H:%M:%S.%f%z" )
        :param in_datetime: datetime object to convert
        :type in_datetime: datetime.datetime
        :return: datetime object's time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
        For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
        :rtype: str
        """
        return in_datetime.strftime(BWAPIHelper.BW_DATE_TIME_PATTERN)

    def total_mentions(self, in_project_id, in_query_id, in_start_datetime_tz, in_end_datetime_tz):
        """
        Retrieves the numbers of mentions between given start and end datetime values.
        One API Call.
        :param in_project_id: The ProjectID.
        :type in_project_id: int
        :param in_query_id: The QueryID.
        :type in_query_id: int
        :param in_start_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
        For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
        Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_start_datetime_tz: str
        :param in_end_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
        For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
        Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_end_datetime_tz: str
        :return: A dictionary containing 'mentionsCount' which gives the count of the number of mentions.
        :rtype: dict
        """
        url = f'https://api.brandwatch.com/projects/{in_project_id}/data/mentions/count'
        params = {"queryId": in_query_id, "startDate": in_start_datetime_tz, "endDate": in_end_datetime_tz}
        response = self.bw_api_caller.call_api(url, params)
        return response

    def mentions_aggregate_over_time(self, in_project_id, in_query_id, in_start_datetime_tz, in_end_datetime_tz,
                                  in_aggregate="volume", in_dimension1="sentiment", in_dimension2="hours"):
        """
        Retrieves aggregated counts over time.

        :param in_project_id: The ProjectID.
        :type in_project_id: int
        :param in_query_id: The QueryID.
        :type in_query_id: int
        :param in_start_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
                                    For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
                                    Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_start_datetime_tz: str
        :param in_end_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
                                    For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
                                    Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_end_datetime_tz: str
        :param in_aggregate: Aggregates such as "volume" , "authors", "domains", "reach".
                            All aggregates allowed are listed at : https://developers.brandwatch.com/docs/chart-dimensions-and-aggregates#aggregates
        :type in_aggregate: str
        :param in_dimension1: Dimensions such as "days", "hours", "countries", "authors", "sentiment"
                            Dimensions allowed are listed at : https://developers.brandwatch.com/docs/chart-dimensions-and-aggregates#dimensions
        :type in_dimension1: str
        :param in_dimension2: Dimensions such as "days", "hours", "countries", "authors", "sentiment"
                            Dimensions allowed are listed at : https://developers.brandwatch.com/docs/chart-dimensions-and-aggregates#dimensions
        :type in_dimension2: str
        :return: Dictionary structure (JSON like) which contains nested chart data.
        :rtype: dict
        """
        print(f"Aggregate : {in_aggregate}, Dimension1 : {in_dimension1}, Dimension2 : {in_dimension2}")
        url = f"https://api.brandwatch.com/projects/{in_project_id}/data/{in_aggregate}/{in_dimension1}/{in_dimension2}"
        response = self.bw_api_caller.call_api(url, {"queryId": in_query_id, "startDate": in_start_datetime_tz, "endDate": in_end_datetime_tz})
        return response
    
    def retrieve_all_mentions(self, in_project_id, in_query_id, in_start_datetime_tz, in_end_datetime_tz):
        """
        Retrieve all mentions for the given duration for the given queue.

        :param in_project_id: The Project ID
        :type in_project_id: int
        :param in_query_id:  The Query ID
        :type in_query_id: int
        :param in_start_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
                                    For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
                                    Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_start_datetime_tz: str
        :param in_end_datetime_tz: Date and time formatted as a string with strftime format : "%Y-%m-%dT%H:%M:%S.%f%z"
                                    For example, 1:00am on 24th of February 2022 in Eastern Standard Timezone (UTC - 5 hours) will be written as : "2022-02-24T01:00:00.000000-0500")
                                    Use the :func:`~bw_api_helper.BWAPIHelper.datetime_to_str` to easily convert datetime objects to this format.
        :type in_end_datetime_tz: str
        :return: A list of pages, each page will contain a maximum of 5000 mentions.
        :rtype: list
        """
        response_list = []
        url = f"https://api.brandwatch.com/projects/{in_project_id}/data/mentions/fulltext"
        params = {"queryId": in_query_id, "startDate": in_start_datetime_tz, "endDate": in_end_datetime_tz, "pageSize": 5000, "orderBy": "date", "orderDirection": "asc"}
        response = self.bw_api_caller.call_api(url, params)
        response_list.append(response)
        while "nextCursor" in response:
            params["cursor"] = response["nextCursor"]
            response = self.bw_api_caller.call_api(url, params)
            response_list.append(response)
        return response_list
