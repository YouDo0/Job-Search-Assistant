from .base import BaseScraper
from bs4 import BeautifulSoup

class IndeedScraper(BaseScraper):
    def search(self, keywords: list, location: str = None) -> list:
        jobs = []
        for keyword in keywords:
            url = f"https://www.indeed.co.id/jobs?q={keyword.replace(' ', '+')}"
            if location:
                url += f"&l={location.replace(' ', '+')}"

            try:
                resp = self.session.get(url, timeout=30)
                soup = BeautifulSoup(resp.text, 'lxml')

                job_cards = soup.select('.jobsearch-ResultsList > li')
                for card in job_cards:
                    try:
                        title_elem = card.select_one('.jobTitle > a')
                        company_elem = card.select_one('.companyName')
                        location_elem = card.select_one('.companyLocation')
                        salary_elem = card.select_one('.salary-snippet-container')

                        if title_elem:
                            job_id = card.get('data-jk', '')
                            salary_min, salary_max = self.extract_salary(salary_elem.text) if salary_elem else (None, None)

                            jobs.append({
                                'external_id': f'indeed_{job_id}',
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': location_elem.text.strip() if location_elem else location or '',
                                'description': '',
                                'source': 'indeed',
                                'source_url': f'https://www.indeed.co.id/viewjob?jk={job_id}' if job_id else '',
                                'seniority': self.detect_seniority(title_elem.text),
                                'salary_min': salary_min,
                                'salary_max': salary_max,
                                'posted_date': None
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"Indeed scraper error: {e}")
                continue

        return jobs
