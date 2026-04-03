from .base import BaseScraper
from bs4 import BeautifulSoup

class JobStreetScraper(BaseScraper):
    def search(self, keywords: list, location: str = None) -> list:
        jobs = []
        for keyword in keywords:
            url = f"https://www.jobstreet.co.id/id/job-search?keywords={keyword.replace(' ', '%20')}"
            if location:
                url += f"&locations={location.replace(' ', '%20')}"

            try:
                resp = self.session.get(url, timeout=30)
                soup = BeautifulSoup(resp.text, 'lxml')

                job_cards = soup.select('[data-automation="normalJob"]')
                for card in job_cards:
                    try:
                        title_elem = card.select_one('[data-automation="jobTitle"]')
                        company_elem = card.select_one('[data-automation="companyName"]')
                        location_elem = card.select_one('[data-automation="location"]')
                        link_elem = card.select_one('a[data-automation="jobTitle"]')

                        if title_elem:
                            href = link_elem.get('href', '') if link_elem else ''
                            job_id = href.split('-')[-1] if href else ''

                            jobs.append({
                                'external_id': f'jobstreet_{job_id}',
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': location_elem.text.strip() if location_elem else location or '',
                                'description': '',
                                'source': 'jobstreet',
                                'source_url': f'https://www.jobstreet.co.id{href}' if href else '',
                                'seniority': self.detect_seniority(title_elem.text),
                                'salary_min': None,
                                'salary_max': None,
                                'posted_date': None
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"JobStreet scraper error: {e}")
                continue

        return jobs
