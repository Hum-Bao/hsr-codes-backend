import os
from github import Github
from github import InputGitTreeElement
from dotenv import load_dotenv

load_dotenv()


def push(PATH, RAW_TXT):
    g = Github(os.getenv("github_token", ""))
    repo = g.get_user().get_repo(os.getenv("github_repo", ""))  # repo name
    file_list = [PATH + "/" + RAW_TXT]
    file_names = [RAW_TXT]
    commit_message = "Python commit"
    master_ref = repo.get_git_ref("heads/main")
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)

    element_list = list()
    for i, entry in enumerate(file_list):
        with open(entry) as input_file:
            data = input_file.read()
        element = InputGitTreeElement(file_names[i], "100644", "blob", data)
        element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)
