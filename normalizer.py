def extract_company_domain(email: str | None, website: str | None) -> str | None:
    FREE_EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', '.edu', '.ac.in']

    if email and email != "":
        email_domain = email.split('@')[1].lower()
        if email_domain not in FREE_EMAIL_DOMAINS:
            return email_domain

    if website and website != "":
        clean_website = (
            website.lower()
            .removeprefix('https://').removeprefix('http://')
            .removeprefix('www.')
            .rstrip('/')
            .split('/')[0]
        )
        if clean_website:
            return clean_website
    
    return None

def normalize_company_name(raw_company: str | None) -> str | None:
    NON_COMPANY_WORDS = ["student", "freelance", "self-employed", "unemployed", "looking for"]
    COMMON_SUFFIXES = [", Inc.", ", LLC", ", Ltd" ]

    if raw_company:
        company = (
            raw_company.removeprefix('@')
            .strip(' ')
        )

        for word in NON_COMPANY_WORDS:
            if word in company.lower():
                return None

        for suffix in COMMON_SUFFIXES:
            company = company.removesuffix(suffix)

        return company
    
    return None


if __name__ == '__main__':
    print('---- email ----')
    print(extract_company_domain(email='abc@gmail.com', website=None))
    print(extract_company_domain(email='xyz@abc.in', website=None))
    print(extract_company_domain(website='http://abc.net/', email=None))
    print(extract_company_domain(website=None, email=None))
    print(extract_company_domain(website='', email=''))

    print('---- company ----')

    print(normalize_company_name(raw_company=None))
    print(normalize_company_name(raw_company='ABC XYZ, Inc.'))
    print(normalize_company_name(raw_company='Google, LLC'))
    print(normalize_company_name(raw_company='QWERTY, Ltd'))
    print(normalize_company_name(raw_company='@student'))
    print(normalize_company_name(raw_company='freelance @Google'))