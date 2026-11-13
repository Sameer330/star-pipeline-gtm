from pydantic import BaseModel
from typing import Optional
import asyncio
import httpx
from dotenv import load_dotenv
import os
from normalizer import extract_company_domain, normalize_company_name

load_dotenv()

github_token = os.getenv('GITHUB_TOKEN')

headers = {
    'User-Agent': 'star-pipeline',
    'Authorization': f'Bearer {github_token}'
}

class DeveloperProfile(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    signal_type: str = "activity"

async def harvest_gh() -> list[DeveloperProfile]:
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.github.com/repos/supabase/supabase/events', headers=headers)
        data = response.json()

        if response.status_code != 200:
            print(f"Error {response.status_code}: response.text")
            return

        seen_users = set()

        leads_list = []

        # first_event = data[0]
        # print(first_event['type'])
        # print(first_event['actor']['login'])
        for event in data[0:30]:
            username = event['actor']['login']
            event_type = event['type']
            if "[bot]" in username:
                continue
            else:
                if username in seen_users:
                    continue

                seen_users.add(username)

                # print(f"Real User: {username} | Action: {event_type}")
                lead = await enrich_profile(client=client, username=username, event_type=event_type)
                # print(lead.model_dump_json(indent=2))
                leads_list.append(lead)

    return leads_list

async def enrich_profile(client: httpx.AsyncClient, username: str, event_type: str) -> DeveloperProfile:
        response = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        profile_data = response.json()

        email = profile_data.get('email')
        website = profile_data.get('blog')
        company = profile_data.get('company')

        if email is None:
             email = await find_commit_email(client=client, username=username)

        website = extract_company_domain(email, website)

        company = normalize_company_name(company)

        return DeveloperProfile(
            username=profile_data.get('login'),
            name=profile_data.get('name'),
            bio=profile_data.get('bio'),
            company=company,
            location=profile_data.get('location'),
            email=email,
            website=website,
            signal_type=event_type,
        )

async def find_commit_email(client: httpx.AsyncClient, username: str) -> str | None:
    response = await client.get(f"https://api.github.com/users/{username}/events/public", headers=headers)

    events = response.json()

    for event in events:
        if event['type'] == "PushEvent":
            payload = event.get('payload', {})
            commits = payload.get('commits', [])

            for c in commits:
                email = c.get('author', {}).get("email")

                if email is None:
                    head_sha = payload.get('head', None)
                    if head_sha:
                        email = find_email_from_head_sha(client=client, username=username, head_sha=head_sha)

                if email and "noreply.github.com" not in email:
                    return email
    return None

async def find_email_from_head_sha(client: httpx.AsyncClient, username: str, head_sha: str) -> str | None:
    response = await client.get(f"https://api.github.com/repos/supabase/supabase/commits/{username}", headers=headers)

    commit_data = response.json()

    commit = commit_data.get('commit', {})

    email = commit.get('author').get('email')

    return email


# Actual execution from terminal starts here
if __name__ == '__main__':
    profile = DeveloperProfile(username='test-user-1')

    # print(profile.model_dump_json())

    # profile2 = DeveloperProfile()
    asyncio.run(harvest_gh())