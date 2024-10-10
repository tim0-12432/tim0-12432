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
    repo_owner = repo_contribution['repository']['owner']['login']
    if repo_owner != USERNAME:
        contributions_in_foreign_repos.append(f"<tr><td><a href='{repo_contribution['repository']['url']}'>{repo_contribution['repository']['name']}</a></td><td>{repo_contribution['contributions']['nodes'][0]['commitCount']}</td></tr>")

with open('README.md', 'r') as file:
    readme_content = file.readlines()

start_marker = "<!-- START_CONTRIBUTIONS -->\n"
end_marker = "<!-- END_CONTRIBUTIONS -->\n"

start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

new_readme_content = readme_content[:start_index] + ['<h3>Contributed to following projects</h3>\n', '<table>'] + contributions_in_foreign_repos + ['\n', '</table>'] + readme_content[end_index:]

with open('README.md', 'w') as file:
    file.writelines(new_readme_content)

print("README.md was successfully updated.")
