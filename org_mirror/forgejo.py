from org_mirror import log

import json
import requests

from base64 import b64encode


class Forgejo:
    def __init__(self, user: str, password: str, url: str):
        self.token = b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
        if not url.startswith("http"):
            self.url = f"https://{url}"
        else:
            self.url = url

    def createOrg(
        self,
        username: str,
        public: str = True,
    ):
        log.info(f"Creating organization {username}")

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "authorization": f"Basic {self.token}",
        }

        if public:
            visibility = "public"
        else:
            visibility = "false"

        data = {"username": username, "visibility": visibility}

        log.debug(data)

        response = requests.post(
            f"{self.url}/api/v1/orgs", headers=headers, data=json.dumps(data)
        )

        if "id" in response.json():
            log.info(f"Organization {username} create successfully!")
            return

        if "user already exists" in response.json()["message"]:
            log.info(f"Organiztion already exists!")
            return

        response.raise_for_status()

        return response.status_code

    def createRepo(
        self,
        org: str,
        name: str,
        public: str = True,
    ):
        log.info(f"Creating repository {name}")

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "authorization": f"Basic {self.token}",
        }

        if public:
            visibility = "public"
        else:
            visibility = "false"

        data = {"name": name, "visibility": visibility}

        log.debug(data)

        response = requests.post(
            f"{self.url}/api/v1/orgs/{org}/repos",
            headers=headers,
            data=json.dumps(data),
        )

        if "id" in response.json():
            log.info(f"Repository {name} create successfully!")
            return

        if "repository with the same name already exists" in response.json()["message"]:
            log.info(f"Repository already exists!")
            return

        response.raise_for_status()

        return response.status_code
