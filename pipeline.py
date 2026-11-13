from harvester import harvest_gh, DeveloperProfile
import subprocess
from pydantic import BaseModel
import json

class LeadData(BaseModel):
    name: str | None
    username: str
    company: str | None
    email: str | None
    website: str | None
    location: str | None
    signal_type: str = "activity"
    tier: str
    confidence: str
    reasoning: str
    suggested_action: str

async def pipeline_gh():
    leads = await harvest_gh()

    clean_leads: list[DeveloperProfile] = []

    for lead in leads:
        if lead.company or lead.website or lead.email:
            clean_leads.append(lead)

    print(f'Original List -> {len(leads)}') 
    print(f'Cleaned List -> {len(clean_leads)}')

    try:
        with open('icp-prompt.txt', 'r', encoding='utf-8') as file:
            icp_prompt = file.read()
    except FileNotFoundError:
        print('File `icp-prompt.txt` not found.')
        return

    lead_data_result: list[LeadData] = []

    for data in clean_leads:
        name = data.name
        username = data.username
        company = data.company
        website = data.website
        signal_type = data.signal_type
        location = data.location
        bio = data.bio
        email = data.email

        formatted_prompt = icp_prompt.format(
            name=name or "N/A",
            username=username or "N/A",
            company=company or "N/A",
            website=website or "N/A",
            signal_type=signal_type or "N/A",
            location=location or "N/A",
            bio=bio or "N/A",
        )

        print(f"Evaluating @{username} with AI...")

        result = subprocess.run(
            ["agy", "-p", formatted_prompt],
            capture_output=True,
            text=True,
        )

        ai_output = json.loads(result.stdout.strip())

        lead_data = LeadData(
            name=name,
            username=username,
            company=company,
            email=email,
            website=website,
            location=location,
            signal_type=signal_type,
            tier=ai_output.get('tier'),
            confidence=ai_output.get('confidence'),
            reasoning=ai_output.get('reasoning'),
            suggested_action=ai_output.get('suggested_action'),
        )

        print(f'name - {name} \nLead Info - {lead_data.model_dump_json(indent=2)}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(pipeline_gh())