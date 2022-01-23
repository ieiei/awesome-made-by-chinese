import time
import urllib.request
import urllib.parse
import json

USER_API = "https://api.github.com/users/"
REPO_API = "https://api.github.com/repos/"

STAR_SPLIT = [1000, 3000, 10000, 30000]

HEADER = """
# :cn: Awesome Made by Chineses [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> Curating the best projects that were made and mainly contributed by Chinese developers

"""

CONTRIBUTE = """
## Contributing

You can easy add project and pull request, just add project in file project.list and the actions will generate the README.

The project format is repo[,author], if the author is not the repo owner. The repo is must in github, but the author need not.

Please make sure that:
- The project was created by the developer born in China or self-indicate themself as Chinese.
- The project is widely used rathe than a experimental or sample project.
- The project can not be a collections or a paper or blog.
- The project has more that 1000 stars on Github, cause the actions will cut the project which under 1000 stars.

"""

THANKS = """
## Thanks

- [🇷🇺 awesome-made-by-russians](https://github.com/gaearon/awesome-made-by-russians)
- [🇧🇷 awesome-made-by-brazilians](https://github.com/felipefialho/awesome-made-by-brazilians)

"""


def get_star_line(star):
    return f"## > {star//1000}k ★\n\n"


def get_user_info(user_name):
    try:
        r = urllib.request.urlopen(urllib.parse.urljoin(USER_API, user_name))
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        pass


def get_repo_info(repo_path):
    try:
        r = urllib.request.urlopen(urllib.parse.urljoin(REPO_API, repo_path))
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        pass



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

    def __repr__(self):
        return self.repo_name

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
    repo_list = []
    with open("project.list", "r") as project_file:
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

    repo_list.sort(reverse=True)
    readme_str = ""
    star_range = 1000000000
    for repo_object in repo_list:
        try:
            while (repo_object.stargazers < star_range):
                star_range = STAR_SPLIT.pop()
                readme_str += get_star_line(star_range)
            readme_str += str(repo_object)
            readme_str += "\n"
        except IndexError:
            break


    with open("README.md", "w") as readme_file:
        readme_file.write(HEADER)
        readme_file.write(readme_str)
        readme_file.write(CONTRIBUTE)
        readme_file.write(THANKS)


if __name__ == '__main__':
    main()
