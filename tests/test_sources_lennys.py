from urllib.parse import parse_qs

import sources


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_lennys_jobs_maps_algolia_hits(monkeypatch):
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = json["params"]
        captured["timeout"] = timeout
        return FakeResponse({
            "hits": [
                {
                    "url": "https://example.com/job",
                    "title": "Senior Python Developer",
                    "job_id": "job-123",
                    "location": "Remote",
                    "company_name": "ExampleCo",
                    "updated_at": "2026-06-09T03:46:37.000Z",
                    "description_tags": ["Python", "AWS"],
                    "salary_range_min": 120,
                    "salary_range_max": 180,
                    "business_description_short": "Cloud infrastructure",
                    "company_description_plus": ["Unicorn", "500 employees"],
                    "job_openings_total": 42,
                    "platform_partner_lenny": 1,
                    "third_party_lists": ["Lenny 100"],
                    "company_investor_details": [{"name": "Example Ventures"}],
                }
            ]
        })

    monkeypatch.setattr(sources.requests, "post", fake_post)
    monkeypatch.setattr(sources.time, "sleep", lambda _: None)
    monkeypatch.setattr(sources.config, "REMOTE_ONLY", True, raising=False)
    monkeypatch.setattr(sources.config, "LENNYS_JOBS_HITS_PER_QUERY", 5, raising=False)

    jobs = sources.fetch_lennys_jobs(["python developer"])

    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Senior Python Developer"
    assert job.company == "ExampleCo"
    assert job.url == "https://example.com/job"
    assert job.source == "lennys_jobs"
    assert job.uid == "lennys_jobs:job-123"
    assert job.salary == "$120K - $180K"
    assert job.posted_date == "2026-06-09T03:46:37.000Z"
    assert "Skills/tools: Python, AWS" in job.description
    assert "Company open roles: 42" in job.description
    assert "Posted by Lenny Community" in job.description
    assert "Lenny 100 company" in job.description
    assert "Investors: Example Ventures" in job.description

    params = parse_qs(captured["params"])
    assert captured["url"] == sources.LENNYS_JOBS_ENDPOINT
    assert captured["headers"]["x-algolia-application-id"] == sources.LENNYS_JOBS_APP_ID
    assert params["query"] == ["python developer"]
    assert params["hitsPerPage"] == ["5"]
    assert "platform_partner_lenny" in params["filters"][0]
    assert "job_locations_combined" in params["filters"][0]
    assert "Engineering (Software)" in params["filters"][0]
