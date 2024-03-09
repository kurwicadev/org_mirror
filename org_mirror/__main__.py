#!/usr/bin/env python3

from org_mirror import log
from org_mirror.forgejo import Forgejo

import os
import shutil

from dotenv import load_dotenv
from git import Repo
from github import Github


load_dotenv()


# Required env variables
ORG = os.getenv("ORG")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FORGEJO_URL = os.getenv("FORGEJO_URL")
FORGEJO_USER = os.getenv("FORGEJO_USER")
FORGEJO_PASSWORD = os.getenv("FORGEJO_PASSWORD")

# Optional env variables
FORGEJO_SSH_PORT = os.getenv("FORGEJO_SSH_PORT", 2022)
REPO_DIR = os.getenv("REPO_DIR", "repositories")


def main():
    log.info("Starting log_mirror")

    log.info("Creating repositories directory")
    if not os.path.exists(REPO_DIR):
        os.mkdir(REPO_DIR)

    forgejo = Forgejo(FORGEJO_USER, FORGEJO_PASSWORD, FORGEJO_URL)
    forgejo.createOrg(ORG)

    github = Github(GITHUB_TOKEN)
    github_repositories = github.get_organization(ORG).get_repos()

    for github_repo in github_repositories:
        log.info(f"Processing repository {github_repo.full_name}")

        repo_path = os.path.join(REPO_DIR, github_repo.full_name)

        forgejo.createRepo(ORG, github_repo.name)

        clone_url = f"git@github.com:{github_repo.full_name}.git"
        forgejo_url = (
            f"ssh://git@{FORGEJO_URL}:{FORGEJO_SSH_PORT}/{github_repo.full_name}.git"
        )

        log.info("Cloning repository")

        repo = Repo.clone_from(clone_url, repo_path, no_single_branch=True)

        # Fetch all branches
        for ref in repo.remotes.origin.refs:
            branch = str(ref).replace("origin/", "")

            if branch == "HEAD":
                continue

            repo.create_head(branch, ref)

        log.info("Creating forgejo remote")
        forgejo_remote = repo.create_remote("forgejo", forgejo_url)

        log.info("Pushing branches")
        forgejo_remote.push(all=True, force=True)

        shutil.rmtree(repo_path)

        log.info("Repository mirrored")

    log.info("All done")


if __name__ == "__main__":
    main()
