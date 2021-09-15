import time
import urllib.request
import urllib.parse
import json

user_api = "https://api.github.com/users/"
repo_api = "https://api.github.com/repos/"


class RepoObject:
    def __init__(self, author_name, author_url, repo_name, repo_url,
                 description, stargazers, language):
        self.author_name = author_name
        self.author_url = author_url
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.description = description
        self.stargazers = stargazers
        self.language = language

    def __str__(self):
        if self.author_url:
            return f"""- **[{self.repo_name}]({self.repo_url})** by [{self.author_name}]({self.author_url})

    {self.description}
            """
        else:
            return f"""- **[{self.repo_name}]({self.repo_url})** by *{self.author_name}*

    {self.description}
            """

    def __lt__(self, other):
        return self.stargazers < other.stargazers

    def __gt__(self, other):
        return self.stargazers > other.stargazers

    def __eq__(self, other):
        return self.stargazers == other.stargazers

    def __le__(self, other):
        return self.stargazers <= other.stargazers

    def __ge__(self, other):
        return self.stargazers >= other.stargazers

    def __ne__(self, other):
        return self.stargazers != other.stargazers


def get_user_info(user_name):
    try:
        r = urllib.request.urlopen(urllib.parse.urljoin(user_api, user_name))
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        pass


def get_repo_info(repo_path):
    try:
        r = urllib.request.urlopen(urllib.parse.urljoin(repo_api, repo_path))
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        pass


def get_repo(repo_path, author):
    repo = get_repo_info(repo_path)
    if not repo:
        return
    repo_name = repo.get('name')
    repo_url = repo.get('html_url')
    description = repo.get("description") or ""
    stargazers = repo.get("stargazers_count")
    language = repo.get("language")

    user_name = author or repo_path.split("/")[0]
    user = get_user_info(user_name)
    if user:
        author_name = user.get("name") or user.get('login')
        author_url = user.get("html_url")
    else:
        author_name = user_name
        author_url = None
    return RepoObject(author_name, author_url, repo_name, repo_url,
                     description, stargazers, language)


def main():
    project_file = open("project.txt", "r")
    repo_list = []
    while True:
        line = project_file.readline()
        if not line:
            break
        line = line.strip().split(',')
        repo_object = None
        if len(line) > 1:
            repo_path, author = line[0].strip(), line[1].strip()
            repo_object = get_repo(repo_path, author)
        elif len(line) == 1:
            repo_path, author = line[0].strip(), None
            repo_object = get_repo(repo_path, author)
        if isinstance(repo_object, RepoObject):
            repo_list.append(repo_object)
    project_file.close()

    repo_list.sort(reverse=True)
    readme_file = open("README.md", "w")
    for repo_object in repo_list:
        readme_file.write(str(repo_object))
        readme_file.write("\n")
    readme_file.close()


if __name__ == '__main__':
    main()
