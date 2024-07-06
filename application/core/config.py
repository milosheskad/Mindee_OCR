from mindee import Client

mindee_client = Client(api_key="2bdd35a8bdc998a2835f0baa79d5e3ad")
my_endpoint = mindee_client.create_endpoint(
    account_name="dmilo6",
    endpoint_name="bill_of_landing",
    version="1"
)
