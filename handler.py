import json
import os
from urllib import request
import requests
import itertools

def api_req(user):
    url = 'https://api.github.com/graphql'
    query = ("""query {
    user(login: "%s") {
    name
    login
    contributionsCollection {
        totalCommitContributions
        restrictedContributionsCount
        totalPullRequestContributions
    }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
        totalCount
    }
    pullRequests(first: 1) {
        totalCount
    }
    issues(first: 1) {
        totalCount
    }
    followers {
        totalCount
    }
    repositories(first: 100, ownerAffiliations: OWNER, orderBy: {direction: DESC, field: STARGAZERS}) {
        totalCount
        nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
            nodes {
            name
            }
        }
        }
    }
    gists(first: 100) {
        nodes {
        id
        files {
            language {
            name
            }
        }
        }
    }
    }
    }

    """ % (user))

    

    r = requests.post(url, json={'query': query}, headers={"Authorization": "token %s" % os.getenv("GITHUB_TOKEN")})
    return json.loads(r.text)["data"]

def github_extract(event, context):
   
  user = "gabrielmartinigit"#os.getenv("GITHUB_USERNAME")
  
  print("user: %s" % (user) )
  repos_contributtion = api_req(user)["user"]["repositoriesContributedTo"]["totalCount"]
  print("repos_contributtion: %s" % (repos_contributtion))
  
  pullRequests = api_req(user)["user"]["pullRequests"]["totalCount"]
  print("pullRequests: %s" % (pullRequests))
  
  followers = api_req(user)["user"]["followers"]["totalCount"]
  print("followers: %s" % (followers))
  
  map_repos = map(lambda o: languages(o) , api_req(user)["user"]["repositories"]["nodes"])
  concat_languages = list(itertools.chain.from_iterable(list(map_repos)))
  distinct_languages = list(set(concat_languages))
  print("languages: ", distinct_languages)

  
def languages(nodes_repo):
    #print(nodes_repo)
    return list(map(lambda u: u["name"] , nodes_repo["languages"]["nodes"]))