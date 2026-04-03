from .base import BaseScraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin

TRACK_B_COMPANIES = {
    'BCA': 'https://www.bca.co.id/career',
    'Bank Mandiri': 'https://www.bankmandiri.co.id/career',
    'Bank BRI': 'https://www.bri.co.id/career',
    'PwC': 'https://www.pwc.com/id/en/careers.html',
    'Deloitte': 'https://www2.deloitte.com/id/en/careers.html',
    'KPMG': 'https://home.kpmg/id/en/home/careers.html',
    'Barito Pacific': 'https://www.baritopacific.com/careers',
}

class CareerPageScraper(BaseScraper):
    def __init__(self, preferences=None, company_career_urls: dict = None):
        super().__init__(preferences)
        self.company_career_urls = company_career_urls or TRACK_B_COMPANIES

    def search(self, keywords: list, location: str = None) -> list:
        all_jobs = []
        for company_name, career_url in self.company_career_urls.items():
            jobs = self._scrape_company_career_page(company_name, career_url, keywords)
            all_jobs.extend(jobs)
        return all_jobs

    def _scrape_company_career_page(self, company_name: str, url: str, keywords: list) -> list:
        jobs = []
        try:
            resp = self.session.get(url, timeout=30)
            soup = BeautifulSoup(resp.text, 'lxml')

            job_links = soup.select('a[href*="job"], a[href*="career"], a[href*="vacancy"]')

            for link in job_links[:20]:
                try:
                    job_title = link.text.strip()
                    if not job_title or len(job_title) < 5:
                        continue

                    href = link.get('href', '')
                    if href and not href.startswith('http'):
                        href = urljoin(url, href)

                    title_lower = job_title.lower()
                    keyword_match = any(kw.lower() in title_lower for kw in keywords)

                    jobs.append({
                        'external_id': f'career_{company_name.lower().replace(" ", "_")}_{len(jobs)}',
                        'title': job_title,
                        'company': company_name,
                        'location': location or 'Indonesia',
                        'description': '',
                        'source': 'career_page',
                        'source_url': href,
                        'seniority': self.detect_seniority(job_title),
                        'salary_min': None,
                        'salary_max': None,
                        'posted_date': None,
                        '_discovered_from': company_name
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"Error scraping {company_name} career page: {e}")

        return jobs

    def discover_career_page(self, company_name: str, linkedin_listing_url: str = None) -> str:
        base_url = f"https://www.{company_name.lower().replace(' ', '')}.com/careers"
        return base_url
