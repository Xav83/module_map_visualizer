# Module Map visualizer

## Requirements

In order to be able to use this python script, you need to have the following elements installed:
- [gh](https://cli.github.com/), GitHub command line interface

You also need to install the python package detailed in the [requirements.txt](requirements.txt) file, for example, by running the following command:
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic use case
python scripts/repository_dependencies.py -o < name_of_your_github_organization >

# Basic use case with private repositories
python scripts/repository_dependencies.py -o < name_of_your_github_organization > --with-private-repository

# Display the help
python scripts/repository_dependencies.py --help
```

Be careful, the private repositories of the GitHUb organisation will be displayed in the graph generated, if you have the GitHub access to those repositories. Take that information into account if you plan on sharing the generated graphs 😉
