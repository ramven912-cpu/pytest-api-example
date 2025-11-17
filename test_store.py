from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

@pytest.fixture
def new_pet():
    all_pets = api_helpers.get_api_data("/pets/")

    # ASSUMPTION: pet_id = len(pets) will always be a free index.
    pet_data = {
        "id": len(all_pets.json()),
        "name": "Test Cat",
        "type": "cat",
        "status": "available"
    }
    pet_response = api_helpers.post_api_data("/pets/", pet_data)

    assert pet_response.status_code == 201
    return pet_response.json()

@pytest.fixture
def new_order(new_pet):
    pet_data = {
        "pet_id": new_pet["id"]
    }
    order_response = api_helpers.post_api_data("/store/order", pet_data)

    assert order_response.status_code == 201
    validate(instance=order_response.json(), schema=schemas.order)
    return order_response.json()

test_patch_parameters = [
    (None, "available", 200),
    (None, "sold", 200),
    (None, "pending", 200),

    (None, 0, 400),
    (None, -1, 400),
    (None, "", 400),

    ("None", "available", 404),
    (" ", "sold", 404),
    (0, "available", 404),
    ("e0862a12-17a3-49eb-8f69-a5d8997f8349", "pending", 404),
]
@pytest.mark.parametrize("order_id,status,response_code", test_patch_parameters)
def test_patch_order_by_id(new_order, order_id, status, response_code):
    if order_id is None:
        order_id = new_order['id']

    test_endpoint = f"/store/order/{order_id}"
    data = {'status': status}

    response = api_helpers.patch_api_data(test_endpoint, data)

    assert response.status_code == response_code
    expected_message = None
    if response_code == 200:
        expected_message = "Order and pet status updated successfully"
    elif response_code == 400:
        expected_message = f"Invalid status '{status}'. Valid statuses are available, sold, pending"
    else:
        expected_message = "Order not found"
    assert expected_message in response.json()['message']
