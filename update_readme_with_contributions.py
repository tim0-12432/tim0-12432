import requests
import os
from datetime import datetime, timedelta

USERNAME = "tim0-12432"
TOKEN = os.getenv("GITHUB_TOKEN")

end_date = datetime.utcnow()
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
    if repo_owner != USERNAME:  # Prüfen, ob der Repository-Besitzer nicht du bist
        contributions_in_foreign_repos.append(f"- [{repo_contribution['repository']['name']}]({repo_contribution['repository']['url']})")

with open('README.md', 'r') as file:
    readme_content = file.readlines()

start_marker = "<!-- START_CONTRIBUTIONS -->\n"
end_marker = "<!-- END_CONTRIBUTIONS -->\n"

start_index = readme_content.index(start_marker) + 1
end_index = readme_content.index(end_marker)

new_readme_content = readme_content[:start_index] + contributions_in_foreign_repos + ['\n'] + readme_content[end_index:]

with open('README.md', 'w') as file:
    file.writelines(new_readme_content)

print("README.md was successfully updated.")
