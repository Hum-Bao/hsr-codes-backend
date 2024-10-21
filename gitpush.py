#import base64
from github import Github
from github import InputGitTreeElement

def push(PATH, RAW_TXT, JSON_TXT):
    #user = "Hum-Bao"
    #password = "Gamerman69!"
    #g = Github(user,password)
    g = Github("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")
    repo = g.get_user().get_repo('StarRail-Giftcodes') # repo name
    file_list = [
        PATH + "/" + RAW_TXT,
        PATH + "/" + JSON_TXT
    ]
    file_names = [
        RAW_TXT,
        JSON_TXT
    ]
    commit_message = 'python commit'
    master_ref = repo.get_git_ref('heads/main')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)

    element_list = list()
    for i, entry in enumerate(file_list):
        with open(entry) as input_file:
            data = input_file.read()
        #if entry.endswith('.png'): # images must be encoded
            #data = base64.b64encode(data)
        element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
        element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)