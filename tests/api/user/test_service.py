import pytest
from pydantic import ValidationError
from api.user.service import do_process

def test_do_process_success(mocker):
    userid = "user001"
    headers = {
        "x-transaction-id": "txn-1234567890"
    }
    body = {
        "name": "Alice",
        "age": 25,
        "birthday": "19990101"
    }

    # モック
    mock_logger = mocker.patch("api.user.service.logger.info")

    # Act
    response = do_process(userid, headers, body)

    # Assert
    assert response["message"] == f"User ID received: {userid}"
    assert response["validated_data"] == body
    mock_logger.assert_called_once()

def test_do_process_invalid_userid():
    with pytest.raises(ValidationError):
        do_process("", {"x-transaction-id": "txn-1234567890"}, {"name": "Bob", "age": 30})