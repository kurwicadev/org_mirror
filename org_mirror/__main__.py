#!/usr/bin/env python3

from org_mirror import args, log
from org_mirror.forgejo import Forgejo

import os
import shutil

from git import Repo
from github import Github

# Required env variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FORGEJO_URL = os.getenv("FORGEJO_URL")
FORGEJO_USER = os.getenv("FORGEJO_USER")
FORGEJO_PASSWORD = os.getenv("FORGEJO_PASSWORD")

# Optional env variables
FORGEJO_SSH_PORT = os.getenv("FORGEJO_SSH_PORT", 2022)
REPO_DIR = os.getenv("REPO_DIR", "repositories")


def mirror_org(org):
    log.info(f"Mirroring {org} from github.com to {FORGEJO_URL}")

    if not os.path.exists(REPO_DIR):
        log.info("Creating repositories directory")
        os.mkdir(REPO_DIR)

    forgejo = Forgejo(FORGEJO_USER, FORGEJO_PASSWORD, FORGEJO_URL)
    forgejo.createOrg(org)

    github = Github(GITHUB_TOKEN)
    github_repositories = github.get_organization(org).get_repos()

    for github_repo in github_repositories:
        log.info(f"Processing repository {github_repo.full_name}")

        repo_path = os.path.join(REPO_DIR, github_repo.full_name)

        forgejo.createRepo(org, github_repo.name)

        clone_url = f"git@github.com:{github_repo.full_name}.git"
        forgejo_url = (
            f"ssh://git@{FORGEJO_URL}:{FORGEJO_SSH_PORT}/{github_repo.full_name}.git"
        )

        log.info("Cloning repository")

        if os.path.exists(repo_path):
            log.warning(f"Path {repo_path} already exists, removing")
            shutil.rmtree(repo_path)

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
        try:
            forgejo_remote.push(all=True, force=True)
        except Exception as e:
            log.warning(f"Failed pushing {github_repo.name}")
            log.exception(e)

        log.info("Repository mirrored")

    log.info(f"Organization {org} mirrored!")


def main():
    log.info("Starting log_mirror")

    for org in args.org:
        mirror_org(org)

    log.info("All done!")


if __name__ == "__main__":
    main()
