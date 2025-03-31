import pytest
from pydantic import ValidationError
from api.user.service import do_process, validate_request

@pytest.mark.parametrize(
    "userid, request_headers, request_body, expected_error_field",
    [
        # userid が空文字（min_lengthエラー）
        ("", {"x-transaction-id": "1234567890"}, {"name": "John", "age": 30}, "userid"),
        # userid が英数字以外を含む（patternエラー）
        ("user!id", {"x-transaction-id": "1234567890"}, {"name": "John", "age": 30}, "userid"),
        # ヘッダーのx-transaction-idが短い（min_lengthエラー）
        ("user123", {"x-transaction-id": "12345"}, {"name": "John", "age": 30}, "x-transaction-id"),
        # ヘッダーのx-transaction-idが存在しない（必須エラー）
        ("user123", {}, {"name": "John", "age": 30}, "x-transaction-id"),
        # body.name が空（min_lengthエラー）
        ("user123", {"x-transaction-id": "1234567890"}, {"name": "", "age": 30}, "name"),
        # body.name が長すぎる（max_lengthエラー）
        ("user123", {"x-transaction-id": "1234567890"}, {"name": "a"*11, "age": 30}, "name"),
        # body.age が数値でない（strict int エラー）
        ("user123", {"x-transaction-id": "1234567890"}, {"name": "John", "age": "thirty"}, "age"),
        # birthday が8桁でない（max_lengthエラー）
        ("user123", {"x-transaction-id": "1234567890"}, {"name": "John", "age": 30, "birthday": "20251"}, "birthday"),
    ]
)
def test_validate_request_validation_error(userid, request_headers, request_body, expected_error_field):
    with pytest.raises(ValidationError) as exc_info:
        validate_request(userid, request_headers, request_body)

    errors = exc_info.value.errors()
    error_fields = [err['loc'][-1] for err in errors]

    # バリデーションエラーが、期待するフィールドで発生していることを確認
    assert expected_error_field in error_fields

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

