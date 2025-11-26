from time import sleep
from flask.testing import FlaskClient
from app import config


def test_rate_limiting(client: FlaskClient, monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT_MAX_REQUESTS", 2)
    monkeypatch.setattr(config, "RATE_LIMIT_COOLDOWN", 3)

    # Make max requests number of requests:
    for i in range(config.RATE_LIMIT_MAX_REQUESTS):
        response = client.get('api/conversations/thread-statuses')
        assert response.status_code == 200
    
    # Make one more
    response = client.get('api/conversations/thread-statuses')
    assert response.status_code == 429

    # Wait for cooldown to pass
    sleep(config.RATE_LIMIT_COOLDOWN)
    
    # Make max requests number of requests:
    for i in range(config.RATE_LIMIT_MAX_REQUESTS):
        response = client.get('api/conversations/thread-statuses')
        assert response.status_code == 200
    
    # Make one more
    response = client.get('api/conversations/thread-statuses')
    assert response.status_code == 429
    