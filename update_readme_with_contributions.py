import requests
import os
from datetime import datetime, timedelta, timezone

USERNAME = "tim0-12432"
TOKEN = os.getenv("GITHUB_TOKEN")

end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=364)

start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

query = f"""
{{
  user(login: "{USERNAME}") {{
    contributionsCollection(from: "{start_date_str}", to: "{end_date_str}") {{
      commitContributionsByRepository {{
        repository {{
          name
          url
          owner {{
            login
            avatarUrl
          }}
        }}
        contributions(first: 100) {{
          nodes {{
            occurredAt
            commitCount
          }}
        }}
      }}
    }}
  }}
}}
"""

headers = {"Authorization": f"Bearer {TOKEN}"}
response = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
data = response.json()

contributions_in_foreign_repos = []
for repo_contribution in data['data']['user']['contributionsCollection']['commitContributionsByRepository']:
    repo_owner = repo_contribution['repository']['owner']
    if repo_owner['login'] != USERNAME:
        commit_count = repo_contribution['contributions']['nodes'][0]['commitCount']
        contributions_in_foreign_repos.append(f"<tr><td><img src='{repo_owner['avatarUrl']}' height='32' width='32' /></td><td><a href='{repo_contribution['repository']['url']}'>{repo_contribution['repository']['name']}</a></td><td>{commit_count} {'commit' if commit_count == 1 else 'commits'}</td></tr>")

with open('README.md', 'r') as file:
    readme_content = file.readlines()

start_marker = "<!-- START_CONTRIBUTIONS -->\n"
end_marker = "<!-- END_CONTRIBUTIONS -->\n"

start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

if len(contributions_in_foreign_repos) == 0:
    print("No contributions found in foreign repositories.")
    new_readme_content = readme_content[:start_index] + readme_content[end_index:]
else:
    new_readme_content = readme_content[:start_index] + ['<h3>Contributed to following projects</h3>\n', '<table>'] + contributions_in_foreign_repos + ['\n', '</table>'] + readme_content[end_index:]

with open('README.md', 'w') as file:
    file.writelines(new_readme_content)

print("README.md was successfully updated.")
