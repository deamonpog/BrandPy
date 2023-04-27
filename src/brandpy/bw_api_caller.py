import time
import requests
import math
import os
from collections import deque
import numpy as np

from .bw_auth_config import BWAuthConfig


class BWAPICaller:

    def __init__(self, in_bw_config, in_last_use=600):
        """
        Initialize BWAPICaller object.
        :param in_bw_config: The BWAuthConfig object that contains the access token.
        :type in_bw_config: BWAuthConfig
        :param in_last_use: Number of seconds since the API was last used with the given token. Default value is 600 which assumes that the API was not called in the last 10 minutes.
        :type in_last_use: float
        """
        self.access_token = in_bw_config.token
        self.queue_file_path = in_bw_config.queue_file_path
        self._queue = deque(maxlen=30)
        """ queue : 30 requests per 10 minutes (600 seconds) """
        if not os.path.exists(self.queue_file_path):
            self._queue.extend((time.time() - in_last_use for i in range(30)))
            np.savetxt(self.queue_file_path, np.array(self._queue), delimiter=",")
        else:
            self._queue.extend(np.loadtxt(self.queue_file_path, delimiter=","))

    def _connect_to_endpoint(self, in_url, in_params):
        auth_header = {"Authorization": f"bearer {self.access_token}"}
        response = requests.request("GET", in_url, headers=auth_header, params=in_params)
        print("Response Status : {} at {}".format(response.status_code, time.time()))
        if response.status_code != 200:
            print(response)
            print(response.json())
            raise Exception(f"Request returned an error: {response.status_code} -> {response.text}")
        return response.json()

    def _wait_rate_limit(self):
        current_time = time.time()
        elapsed_time = current_time - self._queue[0]
        if elapsed_time < 601:
            wait_time = math.ceil(601 - elapsed_time)
            print(f"Waiting for : {wait_time:.2f} seconds ({wait_time/60:.2f} minutes)")
            time.sleep(wait_time)
            current_time = time.time()
        self._queue.append(current_time)
        np.savetxt(self.queue_file_path, np.array(self._queue), delimiter=",")

    def call_api(self, in_url, in_params):
        self._wait_rate_limit()
        json_response = self._connect_to_endpoint(in_url, in_params)
        return json_response
