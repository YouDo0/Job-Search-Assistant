from .base import BaseScraper
from bs4 import BeautifulSoup

class LinkedInScraper(BaseScraper):
    def search(self, keywords: list, location: str = None) -> list:
        jobs = []
        for keyword in keywords:
            url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
            if location:
                url += f"&location={location.replace(' ', '%20')}"

            try:
                resp = self.session.get(url, timeout=30)
                soup = BeautifulSoup(resp.text, 'lxml')

                job_cards = soup.select('.job-card-container')
                for card in job_cards:
                    try:
                        title_elem = card.select_one('.job-card-list__title')
                        company_elem = card.select_one('.job-card-container__company-name')
                        location_elem = card.select_one('.job-card-container__metadata-item')
                        link_elem = card.select_one('a')

                        if title_elem and link_elem:
                            job_id = card.get('data-job-id', '')
                            jobs.append({
                                'external_id': f'linkedin_{job_id}',
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': location_elem.text.strip() if location_elem else location or '',
                                'description': '',
                                'source': 'linkedin',
                                'source_url': link_elem.get('href', ''),
                                'seniority': self.detect_seniority(title_elem.text),
                                'salary_min': None,
                                'salary_max': None,
                                'posted_date': None
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"LinkedIn scraper error for keyword '{keyword}': {e}")
                continue

        return jobs
