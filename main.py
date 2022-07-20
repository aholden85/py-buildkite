import requests
import os


# Ongoing build effort - all functions are translated from API calls documented
# within the following pages:
#   https://buildkite.com/docs/apis/rest-api

# URL encoding
import urllib.parse

# Handling different file/content types
import json

class BuildkiteSession(requests.Session):
    def __init__(self, *args, **kwargs):
        super(BuildkiteSession, self).__init__(*args, **kwargs)
    
    def init_basic_auth(self, api_access_token):
        self.headers.update(
            {
                'Authorization': f'Bearer {api_access_token}'
            }
        )

class BuildkiteClient:
    def __init__(self, api_access_token):
        # Initialize the session.
        self.__session = BuildkiteSession()

        self.__session.init_basic_auth(api_access_token)
        self.__endpoint = "https://api.buildkite.com"

    def __request(
        self,
        method,
        path,
        version = 2,
        params = None,
        data = None,
        headers = {}
    ):
        """Basic function to remove this snippet of code out of every other
        function.

        Args:
            method:     string, what type of request is being made
                        (ie - GET, POST, DELETE).
            path:       string, the target API URL.
            params:     dict, any data that needs to be sent through a query
                        string.
            data:       dict, any data that needs to be sent through the message
                        body rather than through parameters in the query string.
                        Only required for POST, PUT, and PATCH.
            headers:    dict, any extra headers to add to the base auth headers.
        """
        # There are a specific set of request types that can be executed.
        valid_methods = [
            "GET",
            "OPTIONS",
            "HEAD",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]
        if method not in valid_methods:
            raise ValueError(
                f'BuildkiteClient.__request: method must be one of {valid_methods}.'
            )

        req = requests.Request(
            method=method,
            url=f"{self.__endpoint}/v{version}/{path}",
            params=params,
            data=data,
            headers=headers,
        )

        # If any data is being passed, it will need to have the Content-Type header set.
        if data is not None:
            req.headers['Content-Type'] = 'application/json'

        # Execute the request, and return the JSON payload.
        prep = self.__session.prepare_request(req)
        resp = self.__session.send(prep)
        return resp

    def list_organizations(self) -> requests.Response:
        """Returns a paginated list of the user's organizations.
        """
        return self.__request(
            method='GET',
            path=f'organizations'
        )

    def get_organization(self, slug) -> requests.Response:
        """ Returns the details of a specific organization.

        Args:
            slug (str): The organization slug is a simplified version of the
                        organisation name. You can find this within the full
                        details of an organization using list_organizations().
        """
        return self.__request(
            method='GET',
            path=f'organizations/{slug}'
        )

    def list_pipelines(self, slug) -> requests.Response:
        """ Returns a paginated list of an organization's pipelines.

        Args:
            slug (str): The organization slug is a simplified version of the
                        organisation name. You can find this within the full
                        details of an organization using list_organizations().
        """
        return self.__request(
            method='GET',
            path=f'organizations/{slug}/pipelines'
        )


# Example for using the API.

# Fetch the Buildkite API Token from the env variable "BUILDKITE_TOKEN"
buildkite_token = os.environ["BUILDKITE_TOKEN"]

# Create the Buildkite Client object
bk_client = BuildkiteClient(buildkite_token)

# Fetch the slug of the first organization for the specified API token.
org_slug = bk_client.list_organizations().json()[0]['slug']

# Fetch the pipelines
org_pipelines = bk_client.list_pipelines(org_slug).json()

# Print the name of all pipelines for this organization.
for pipeline in org_pipelines:
    print(pipeline['name'])
