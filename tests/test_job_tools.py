"""Tool tests run without an LLM: tools are plain functions, so test them like any other code."""
from jobpilot.repositories.job_repository import InMemoryJobRepository
from jobpilot.tools.job_tools import get_job_details, search_jobs


def test_search_filters_by_location_and_experience():
    jobs = InMemoryJobRepository().search("llm genai", location="remote", experience_years=3)
    assert [job.job_id for job in jobs] == ["JOB-1003"]


def test_search_returns_a_hint_when_nothing_matches():
    result = search_jobs.invoke({"keywords": "cobol mainframe"})
    assert "message" in result[0]


def test_unknown_job_returns_an_error_the_llm_can_act_on():
    result = get_job_details.invoke({"job_id": "JOB-9999"})
    assert "search_jobs" in result["error"]
