import json
import os
import boto3
import requests
import itertools



def get_secret():

    secret_name = os.getenv("SECRET")
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
        , region_name="us-east-1"
    )

    return client.get_secret_value(
            SecretId=secret_name
    )['SecretString']
    
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

    GITHUB_TOKEN = json.loads(get_secret())["GITHUB_TOKEN"]
    r = requests.post(url, json={'query': query}, headers={"Authorization": "token %s" % GITHUB_TOKEN})
    return json.loads(r.text)["data"]

def github_extract(event, context):
  
  user = "gabrielmartinigit"#os.getenv("GITHUB_USERNAME")

  print("user: %s" % (user) )
  
  user_data = api_req(user)
  repos_contributtion = user_data["user"]["repositoriesContributedTo"]["totalCount"]
  print("repos_contributtion: %s" % (repos_contributtion))
  
  pullRequests = user_data["user"]["pullRequests"]["totalCount"]
  print("pullRequests: %s" % (pullRequests))
  
  followers = user_data["user"]["followers"]["totalCount"]
  print("followers: %s" % (followers))
  
  map_repos = map(lambda o: languages(o) , user_data["user"]["repositories"]["nodes"])
  concat_languages = list(itertools.chain.from_iterable(list(map_repos)))
  distinct_languages = list(set(concat_languages))
  print("languages: ", distinct_languages)

  firehose = boto3.client("firehose", region_name="us-east-1")
    
  firehose.put_record(
                DeliveryStreamName=os.getenv("FIREHOSE"),
                Record={ "Data":json.dumps(user_data)},
            )
def languages(nodes_repo):
    #print(nodes_repo)
    return list(map(lambda u: u["name"] , nodes_repo["languages"]["nodes"]))