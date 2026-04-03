from .base import BaseScraper
from bs4 import BeautifulSoup

class GlintsScraper(BaseScraper):
    def search(self, keywords: list, location: str = None) -> list:
        jobs = []
        for keyword in keywords:
            url = f"https://www.glints.com/id/jobs?query={keyword.replace(' ', '%20')}"

            try:
                resp = self.session.get(url, timeout=30)
                soup = BeautifulSoup(resp.text, 'lxml')

                job_cards = soup.select('.job-card')
                for card in job_cards:
                    try:
                        title_elem = card.select_one('.job-title')
                        company_elem = card.select_one('.company-name')
                        location_elem = card.select_one('.location')
                        link_elem = card.select_one('a')

                        if title_elem:
                            href = link_elem.get('href', '') if link_elem else ''
                            job_id = href.split('-')[-1] if href else ''

                            jobs.append({
                                'external_id': f'glints_{job_id}',
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': location_elem.text.strip() if location_elem else location or '',
                                'description': '',
                                'source': 'glints',
                                'source_url': href if href.startswith('http') else f'https://www.glints.com{href}',
                                'seniority': self.detect_seniority(title_elem.text),
                                'salary_min': None,
                                'salary_max': None,
                                'posted_date': None
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"Glints scraper error: {e}")
                continue

        return jobs
