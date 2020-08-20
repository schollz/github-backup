import json
import os
from datetime import date

import click
from tqdm import tqdm
import requests
from loguru import logger

github_user = ""
github_token = ""
backup_folder = date.today().strftime("%Y%m%d")


def github_collect_repos():
    # collect all repos
    logger.info("collecting all repos...")
    try:
        os.mkdir(os.path.join(backup_folder, "repos"))
    except:
        pass
    numDownloaded = 0
    for i in range(1, 30):
        reposjson = os.path.join(
            os.path.join(backup_folder, "repos", "{}.json".format(i))
        )
        if os.path.exists(reposjson):
            continue
        response = requests.get(
            "https://api.github.com/user/repos?page={}&per_page=100&type=owner".format(
                i
            ),
            headers={"Accept": "application/vnd.github.wyandotte-preview+json"},
            auth=(github_user, github_token),
        )
        if len(response.json()) == 0:
            break
        numDownloaded += len(response.json())
        with open(reposjson, "w") as f:
            f.write(json.dumps(response.json(), indent=4))
    if numDownloaded > 0:
        logger.info(f"collected {numDownloaded} repos")

    repolist = {}
    with open(os.path.join(backup_folder, "repos.txt"), "w") as f:
        for i in range(1, 20):
            try:
                a = json.load(
                    open(
                        os.path.join(backup_folder, "repos", "{}.json".format(i)), "rb"
                    )
                )
                b = a[0]["name"]
            except:
                continue
            for repo in a:
                if repo["fork"]:
                    continue
                if repo["name"] in repolist:
                    continue
                f.write(repo["name"] + "\n")
                repolist[repo["name"]] = True
    numDownloaded = len(repolist)
    logger.info(f"found {numDownloaded} repos")


def github_init_migration():
    # start migration
    logger.info("initiating migration...")
    try:
        os.mkdir(os.path.join(backup_folder, "backup"))
    except:
        pass
    with open(os.path.join(backup_folder, "repos.txt"), "r") as f:
        for line in f:
            line = line.strip()
            try:
                os.mkdir(os.path.join(backup_folder, "backup", line))
            except:
                pass
            migrationjson = os.path.join(
                backup_folder, "backup", line, "migration.json"
            )
            datatargz = os.path.join(backup_folder, "backup", line, "data.tar.gz")
            if os.path.exists(migrationjson):
                continue
            if os.path.exists(datatargz):
                continue
            data = '{"repositories":["' + line + '"],"exclude_attachments":true}'
            response = requests.post(
                "https://api.github.com/user/migrations",
                headers={"Accept": "application/vnd.github.wyandotte-preview+json"},
                data=data,
                auth=(github_user, github_token),
            )
            with open(migrationjson, "w") as f2:
                f2.write(json.dumps(response.json(), indent=4))
            break


def github_download_migration():
    # # check if migration is done and then download
    while True:
        finished = True
        with open(os.path.join(backup_folder, "repos.txt"), "r") as f:
            for line in f:
                line = line.strip()
                migrationjson = os.path.join(
                    backup_folder, "backup", line, "migration.json"
                )
                datatargz = os.path.join(backup_folder, "backup", line, "data.tar.gz")
                if not os.path.exists(migrationjson):
                    continue
                if os.path.exists(datatargz):
                    continue
                data = json.load(open(migrationjson, "rb"))
                # check it
                logger.info("checking {}".format(line))
                response = requests.get(
                    "https://api.github.com/user/migrations/{}".format(data["id"]),
                    headers={"Accept": "application/vnd.github.wyandotte-preview+json"},
                    auth=(github_user, github_token),
                )
                try:
                    if response.json()["state"] != "exported":
                        continue
                    else:
                        finished = False
                except:
                    logger.info(response.json())
                    continue
                logger.info("initiating download for {}".format(line))
                response = requests.get(
                    "https://api.github.com/user/migrations/{}/archive".format(
                        data["id"]
                    ),
                    headers={"Accept": "application/vnd.github.wyandotte-preview+json"},
                    auth=(github_user, github_token),
                    stream=True,
                )
                with open(datatargz, "wb") as handle:
                    with tqdm(
                        total=int(response.headers["Content-Length"]),
                        unit="B",
                        unit_scale=True,
                    ) as pbar:
                        for block in response.iter_content(1024):
                            if block:
                                pbar.update(1024)
                                handle.write(block)
                logger.info("downloaded {}".format(line))
        if finished:
            break


@click.command()
@click.option("--user", required=True, help="Github user name")
@click.option("--token", required=True, help="Github token with admin access")
@click.option("--folder", default="backups", help="folder to store backups")
def run(user, token, folder):
    global backup_folder, github_user, github_token
    backup_folder = os.path.join(folder, backup_folder)
    github_user = user
    github_token = token
    logger.info(f"backing up '{user}' repos in '{backup_folder}'")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    github_collect_repos()
    github_init_migration()
    github_download_migration()


if __name__ == "__main__":
    run()
