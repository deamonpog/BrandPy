import errno
import os
import datetime
import json
import time
import getpass
import requests
import pandas as pd

import pathlib
import typing


class BWAuthConfig:
    def __init__(self, in_token_file_path, in_queue_file_path=None, in_prompt_if_failed=True):
        """
        Either reads the token from existing file location or requests a new token from Brandwatch and saves the token to the given file path.

        :param in_token_file_path: Path to the json file that stores the access token information
        :type in_token_file_path: Union[str, os.PathLike]
        :param in_prompt_if_failed: If set True, prompts for username & password in case the token file is not found in
                the given path and requests a token from Brandwatch and saves the newly received token in the path specified.
                If set False, throws FileNotFoundError in case token file is not found in the given path.
        :type in_prompt_if_failed: bool
        :param in_queue_file_path: The path to the file that will work as your queue time database for rate limit management.
        :type in_queue_file_path: str
        """
        # create token file if not exist
        if in_queue_file_path is None:
            self.queue_file_path = os.path.abspath(os.path.join(os.path.dirname(in_token_file_path), "BWQueryQueue.csv"))
        else:
            self.queue_file_path = in_queue_file_path
        self.token_file_path = in_token_file_path
        if not os.path.exists(self.token_file_path):
            print("Token file does not exist.")
            if in_prompt_if_failed:
                print("Retrieving token from Brandwatch API...")
                response = self.__get_token()
                self.__save_token(response)
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.token_file_path)
        # read token from file
        self.__read_token()

    def __save_token(self, in_response):
        if 200 == in_response.status_code:
            print("Successfully got the API token.")
            token_data = in_response.json()
            token_data["e-mail"] = self.email
            token_data["expire_on"] = token_data['expires_in'] + time.time()
            token_data["queue_file"] = self.queue_file_path
            with open(self.token_file_path, 'w', encoding="utf-8") as fout:
                fout.write(json.dumps(token_data))
                expdate = datetime.datetime.fromtimestamp(token_data["expire_on"])
                print("Token Saved. Usable untill : {}.".format(expdate))
        else:
            print("Failed to get API token.")
            print(in_response)
            print(in_response.json())
            raise Exception("Failed to get API token. {}".format(in_response.json()))

    def __read_token(self):
        print("Reading form Token file...")
        with open(self.token_file_path, encoding="utf-8") as fin:
            jsdata = json.load(fin)
        self.email = jsdata["e-mail"]
        token = jsdata["access_token"]
        expiry = jsdata["expire_on"]
        # make sure it doesn't expire for at least an hour
        print(f"Token belongs to : {self.email}")
        print("Token Expires by : {}".format(datetime.datetime.fromtimestamp(expiry)))
        self.token = jsdata["access_token"]
        self.queue_file_path = jsdata["queue_file"]

    def __get_token(self):
        """
        Prompts the user to enter username and password for retrieving the token from Brandwatch API.
        :return:
        :rtype:
        """
        self.email = input("Enter your username: ")
        pwd = getpass.getpass(prompt="Enter password (program doesn't save this): ")
        url = f'https://api.brandwatch.com/oauth/token?username={self.email}&grant_type=api-password&client_id=brandwatch-api-client'
        response = requests.request("POST", url, params={"password": pwd})
        del pwd
        return response
