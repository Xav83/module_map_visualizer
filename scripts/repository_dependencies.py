import argparse
import os
import re
import sys

from gh_cli_adapter import GhCliAdapter
import graphviz


class Repository:
    name = ""
    owner = ""
    submodules = []
    is_submodule_of = []

    def __init__(self, owner, repository_name):
        self.owner = owner
        self.name = repository_name
        self.submodules = []
        self.is_submodule_of = []

    def add_submodule(self, submodule_name_with_owner):
        self.submodules.append(submodule_name_with_owner)

    def reference_this_as_submodule(self, repository_name_with_owner):
        self.is_submodule_of.append(repository_name_with_owner)


def extract_owner_from_submodule_url(url, owner_of_repo):
    if url.startswith("https://"):
        return url.split("/")[-2]
    if url.startswith("../"):
        return owner_of_repo
    if url.startswith("git"):
        return url.split("/")[-2].split(":")[-1]
    print(f"Error: structure of this submodule url is not supported: {url}")
    sys.exit(1)


def generate_graphical_representation_for_repositories_relationship(
    owner, submodule_relationship
):
    print("Generating the Graphviz documents:")
    dot = graphviz.Digraph(comment=f"The {owner} Repo Relationships")

    with dot.subgraph() as top_repo:
        top_repo.attr(rank="same")

        for repo_name, repo_data in submodule_relationship.items():
            if len(repo_data.is_submodule_of) == 0:
                top_repo.node(repo_name)

    with dot.subgraph() as repo_without_submodules:
        repo_without_submodules.attr(rank="same")

        for repo_name, repo_data in submodule_relationship.items():
            if len(repo_data.submodules) == 0:
                repo_without_submodules.node(repo_name)

    for repo_name, repo_data in submodule_relationship.items():
        if repo_data.submodules is not None:
            dot.node(repo_name)
            for submodule in repo_data.submodules:
                dot.edge(repo_name, submodule)
    dot = dot.unflatten(stagger=15)
    print("- Rendering....")
    dot.render(view=True)


def main():
    parser = argparse.ArgumentParser(
        prog="Repositories relationships",
        description="Generates a graphical representation of the relationship between the repositories of a GitHub organization",
        epilog="by Xavier Jouvenot",
    )

    parser.add_argument(
        "-o", "--owner", nargs="?", required=True, default=None, type=str
    )
    parser.add_argument(
        "-pr",
        "--with-private-repository",
        nargs="?",
        required=False,
        default=False,
        type=bool,
    )
    args = parser.parse_args()

    downloaded_gitmodules_location = "tmp/.gitmodules"
    submodule_relationship = {}
    # list all submodules of an organization
    # gh search code \.git --owner args.owner --filename .gitmodules --json repository,textMatches
    matches = GhCliAdapter.search_code(
        "", args.owner, matching_filename=False, filename=".gitmodules"
    )

    if len(matches) == 0:
        print(
            f"No repositories with submodule found for the organisation '{args.owner}'"
        )
        sys.exit(0)

    print("Collecting the data for the repositories:")
    for match in matches:
        if (
            args.with_private_repository is False
            and match["repository"]["isPrivate"] is True
        ):
            continue
        current_repository_with_owner = match["repository"]["nameWithOwner"]
        print(f"- {current_repository_with_owner}")
        # Get the content of the file .gitmodules for the repository "match['repository']['nameWithOwner']"
        owner, repository = current_repository_with_owner.split("/")
        GhCliAdapter.download_file(
            owner, repository, match["path"], downloaded_gitmodules_location
        )

        if current_repository_with_owner not in submodule_relationship:
            submodule_relationship[current_repository_with_owner] = Repository(
                owner, repository
            )

        # Parse the file content to extract all submodules
        with open(
            downloaded_gitmodules_location, encoding="utf-8"
        ) as current_gitmodule:
            matches = re.findall(r"url\s+=\s+.*", current_gitmodule.read())
            for match in matches:
                url = match.split(" ")[-1]
                owner = extract_owner_from_submodule_url(url, owner)
                repo = url.split("/")[-1].replace(".git", "")
                submodule = f"{owner}/{repo}"
                submodule_relationship[current_repository_with_owner].add_submodule(
                    submodule
                )
                if submodule not in submodule_relationship:
                    submodule_relationship[submodule] = Repository(owner, repo)
                submodule_relationship[submodule].reference_this_as_submodule(
                    current_repository_with_owner
                )
        os.remove(downloaded_gitmodules_location)

    # create a graph of relationship
    generate_graphical_representation_for_repositories_relationship(
        args.owner, submodule_relationship
    )


if __name__ == "__main__":
    sys.exit(main())  # next section explains the use of sys.exit
