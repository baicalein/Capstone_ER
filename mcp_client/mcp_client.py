from mcp import ClientSession # pip install mcp
from mcp.client.streamable_http import streamable_http_client


class MCPClient:

    def __init__(self, url="http://localhost:8000/mcp"):
        self.url = url


    async def search(self, resource_type, search_param):

        async with streamable_http_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:

                result = await session.call_tool(
                    "search",
                    {
                        "type": resource_type,
                        "searchParam": search_param
                    }
                )

                return result