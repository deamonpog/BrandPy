import errno
import os
import datetime
import json
import time
import getpass
import requests


# import pathlib
# import typing


class BWAuthConfig:

    @staticmethod
    def request_new_token(in_email, in_pwd):
        url = f'https://api.brandwatch.com/oauth/token?username={in_email}&grant_type=api-password&client_id=brandwatch-api-client'
        response = requests.request("POST", url, params={"password": in_pwd})
        response.raise_for_status()
        # if 200 != response.status_code:
        #     print("Failed to get API token.")
        #     print(response)
        #     print(response.json())
        #     raise Exception("Failed to get API token. {}".format(response.json()))
        # else:
        #     print("Successfully got the API token.")
        return response.json()

    @staticmethod
    def save_token_data_to_file(in_email, in_token_file_path, in_queue_file_path, in_token_json):
        in_token_json["e-mail"] = in_email
        in_token_json["expire_on"] = in_token_json['expires_in'] + time.time()
        in_token_json["queue_file"] = in_queue_file_path
        with open(in_token_file_path, 'w', encoding="utf-8") as fout:
            fout.write(json.dumps(in_token_json))
            expiry_date = datetime.datetime.fromtimestamp(in_token_json["expire_on"])
            print("Token Saved. Usable untill : {}.".format(expiry_date))

    def __init__(self, in_token_file_path, in_queue_file_path=None, in_prompt_if_failed=False):
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
        self.token = None
        self.email = None
        if in_queue_file_path is None:
            self.queue_file_path = os.path.abspath(
                os.path.join(os.path.dirname(in_token_file_path), "BWQueryQueue.csv"))
        else:
            self.queue_file_path = in_queue_file_path
        self.token_file_path = in_token_file_path
        if not os.path.exists(self.token_file_path):
            print("Token file does not exist.")
            if in_prompt_if_failed:
                print("Retrieving token from Brandwatch API...")
                response_json = self.prompt_and_get_token()
                BWAuthConfig.save_token_data_to_file(self.email, self.token_file_path, self.queue_file_path, response_json)
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.token_file_path)
        # read token from file
        self.read_token_data_from_file()

    def read_token_data_from_file(self):
        print("Reading form Token file...")
        with open(self.token_file_path, encoding="utf-8") as fin:
            user_token_data = json.load(fin)
        self.email = user_token_data["e-mail"]
        token = user_token_data["access_token"]
        expiry = user_token_data["expire_on"]
        # make sure it doesn't expire for at least an hour
        print(f"Token belongs to : {self.email}")
        print("Token Expires by : {}".format(datetime.datetime.fromtimestamp(expiry)))
        self.token = user_token_data["access_token"]
        self.queue_file_path = user_token_data["queue_file"]

    def prompt_and_get_token(self):
        """
        Prompts the user to enter username and password for retrieving the token from Brandwatch API.
        :return:
        :rtype:
        """
        self.email = input("Enter your username: ")
        pwd = getpass.getpass(prompt="Enter password (program doesn't save this): ")
        response_json = BWAuthConfig.request_new_token(self.email, pwd)
        del pwd
        return response_json
