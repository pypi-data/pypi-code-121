import argparse
import csv
from datetime import datetime

import httpx
import trio

PROFILE_ENDPOINT = "https://api.github.com/users/{username}"
REPOS_ENDPOINT = "https://api.github.com/users/{username}/repos"
COMMITS_ENDPOINT = "https://api.github.com/repos/{username}/{repo}/commits"


async def extract_emails(login: str, client: httpx.AsyncClient, output: dict):
	emails_uncovered = set()
	resp = await client.get(PROFILE_ENDPOINT.format(username=str(login)))
	if (resp.status_code == 403):
		raise Exception("Rate limited")
	try:
		display_name = resp.json()["name"]
	except KeyError:
		raise Exception("Invalid username")
	response = (await client.get(
		REPOS_ENDPOINT.format(username=str(login)))).json()
	for repo in response:
		if not repo["fork"]:
			repo_name = repo["name"]
			commit_resp = (await client.get(COMMITS_ENDPOINT.format(
				username=str(login), repo=repo_name))).json()
			if not commit_resp:
				continue
			for commit in commit_resp:
				for key in {"committer", "author"}:
					if commit["commit"][str(key)]["name"] == display_name:
						email = commit["commit"][str(key)]["email"]
						if "@users.noreply.github.com" not in email:
							emails_uncovered.add(email)
	if (len(emails_uncovered) > 0):
		output.update({"Scraped Emails": str(', '.join(emails_uncovered))})
	else:
		output.update({"Scraped Emails": "None"})


async def get_profile(login: str, client: httpx.AsyncClient, output: dict):
	resp = (await client.get(PROFILE_ENDPOINT.format(username=str(login)))).json()
	try:
		output.update({
			"Account Creation Date": str(datetime.strptime(str(resp["created_at"]), "%Y-%m-%dT%H:%M:%SZ").strftime('%x')),
			"GitHub Account ID": str(resp["id"]),
			"Avatar URL": str(resp["avatar_url"]),
			"Display Name": str(resp.get("name", "None")),
			"Location": str(resp.get("location", "None")),
			"Public Email": str(resp.get("email", "None")),
			"Twitter Username": str(resp.get("twitter_username", "None")),
			"Public Repo(s)": str(resp["public_repos"]),
			"Public Gist(s)": str(resp["public_gists"]),
			"Bio": str(resp.get("bio", "None"))
		})
	except:
		print(resp)


async def core():
	parser = argparse.ArgumentParser()
	parser.add_argument("target", help="Target to perform OSINT on")
	parser.add_argument("--creds", metavar="username:access_token", dest="creds",
						help="Your username and personal access token to use for requests (prevents rate limiting)", required=False)
	args = parser.parse_args()

	if (args.creds is not None):
		client = httpx.AsyncClient(auth=tuple(str(args.creds).split(':')))
	else:
		client = httpx.AsyncClient()
	try:
		out = dict()
		await get_profile(str(args.target), client, out)
		await extract_emails(str(args.target), client, out)
		print(str(out))
	except Exception as exc:
		print(exc)


def main():
	trio.run(core)
