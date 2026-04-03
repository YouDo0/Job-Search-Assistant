from .base import BaseScraper
from bs4 import BeautifulSoup

class KalibrrScraper(BaseScraper):
    def search(self, keywords: list, location: str = None) -> list:
        jobs = []
        for keyword in keywords:
            url = f"https://www.kalibrr.id/id-ID/jobs?query={keyword.replace(' ', '%20')}"

            try:
                resp = self.session.get(url, timeout=30)
                soup = BeautifulSoup(resp.text, 'lxml')

                job_cards = soup.select('.k-bordered-list-item')
                for card in job_cards:
                    try:
                        title_elem = card.select_one('.k-text-h4')
                        company_elem = card.select_one('.k-text-body1')
                        location_elem = card.select_one('.k-text-body2')
                        link_elem = card.select_one('a')

                        if title_elem:
                            href = link_elem.get('href', '') if link_elem else ''
                            job_id = href.split('-')[-1] if href else ''

                            jobs.append({
                                'external_id': f'kalibrr_{job_id}',
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': location_elem.text.strip() if location_elem else location or '',
                                'description': '',
                                'source': 'kalibrr',
                                'source_url': href if href.startswith('http') else f'https://www.kalibrr.id{href}',
                                'seniority': self.detect_seniority(title_elem.text),
                                'salary_min': None,
                                'salary_max': None,
                                'posted_date': None
                            })
                    except Exception:
                        continue
            except Exception as e:
                print(f"Kalibrr scraper error: {e}")
                continue

        return jobs
