#!/usr/bin/env python
import os
import subprocess

repo_paths = ('sample_repo_1',
                'sample_repo_1',
                    'sample_repo_1')


def execute_pull(repo_path):
    print(f"********* Starting pull: {repo_path} *****************")
    subprocess.check_call("git pull", shell=True, cwd=repo_path)

def execute_gradle_build(repo_path):
    print(f"********* Starting gradle clean build: {repo_path} *****************")
    subprocess.check_call('gradlew clean build', shell=True, cwd=repo_path)


if __name__ == "__main__":
    print(f"********* Starting Repo Update *****************")
    for repo in repo_paths:
        if os.path.isdir(repo):
            execute_pull(repo)
            execute_gradle_build(repo)
        else:
            print(f"The directory {repo} doesn't exist!!!")

    print(f"********* Updating finished successfully!!! *****************")