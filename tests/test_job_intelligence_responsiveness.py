from datetime import datetime, timezone

from job_intelligence import build_responsiveness_intelligence, rank_responsive_targets

UTC = timezone.utc  # noqa: UP017 - local project venv is Python 3.10


def test_build_responsiveness_intelligence_favors_warm_fresh_sources():
    job = {
        "title": "Senior Platform Engineer",
        "company": "FastCo",
        "source": "lennys_jobs",
        "posted_date": datetime.now(UTC).isoformat(),
        "salary": "$160K - $210K",
        "url": "https://job-boards.greenhouse.io/fastco/jobs/123",
        "location": "Remote",
        "description": (
            "Posted by Lenny Community. Lenny 100 company. "
            "Company open roles: 42. Last raised 2mo ago."
        ),
    }
    applications = [{"company": "FastCo", "status": "Interview"}]

    intel = build_responsiveness_intelligence(job, match_score=0.84, applications=applications)

    assert intel["score"] >= 80
    assert intel["label"] == "High response target"
    assert "Technical recruiter" in intel["recruiter_targets"]
    assert any("Lenny Community" in reason for reason in intel["reasons"])
    assert any(link["label"] == "LinkedIn recruiter search" for link in intel["search_links"])
    assert "Senior Platform Engineer" in intel["outreach_note"]


def test_rank_responsive_targets_aggregates_by_company():
    fresh_date = datetime.now(UTC).isoformat()
    jobs = [
        (
            {
                "title": "Cloud Engineer",
                "company": "FastCo",
                "source": "greenhouse",
                "posted_date": fresh_date,
                "url": "https://boards.greenhouse.io/fastco/jobs/1",
            },
            0.8,
        ),
        (
            {
                "title": "SRE",
                "company": "FastCo",
                "source": "lever",
                "posted_date": fresh_date,
                "url": "https://jobs.lever.co/fastco/2",
            },
            0.72,
        ),
    ]

    targets = rank_responsive_targets(jobs, applications=[])

    assert len(targets) == 1
    assert targets[0]["company"] == "FastCo"
    assert targets[0]["job_count"] == 2
    assert targets[0]["score"] >= 65
