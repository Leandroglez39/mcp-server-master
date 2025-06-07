# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import csv
import os

from dotenv import load_dotenv
load_dotenv()

async def main():
    server_params = StdioServerParameters(
        command="python",
        # Make sure to update to the full absolute path to your math_server.py file
        args=["teams/xyz/server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            #agent = create_react_agent("openai:gpt-4.1", tools)
            agent = create_react_agent("google_genai:gemini-2.0-flash", tools)
            agent_response = await agent.ainvoke({"messages": "Search for information about Donald Trump's tariff policies for all countries. Based on the results, create and return a CSV format with columns: country,value. Include the headers in the first row. Format the response as actual CSV data."})
            responses = agent_response.get("messages", [])
            
            # Process the response
            csv_content = responses[-1].content
            
            # Clean the CSV content - remove duplicate headers and extra text
            lines = csv_content.strip().split('\n')
            cleaned_lines = []
            header_found = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('country,value'):
                    if not header_found:
                        cleaned_lines.append(line)
                        header_found = True
                elif line and ',' in line and not line.startswith('```'):
                    # Remove percentage signs from values
                    cleaned_line = line.replace('%', '')
                    cleaned_lines.append(cleaned_line)
            
            # Save to CSV file
            output_file = "/Users/TomeuPM/UNAV/GenAI/trump_tariffs.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                for line in cleaned_lines:
                    csvfile.write(line + '\n')
            
            print(f"CSV data saved to: {output_file}")
            print("Preview of the data:")
            for i, line in enumerate(cleaned_lines[:5]):
                print(line)
            if len(cleaned_lines) > 5:
                print(f"... and {len(cleaned_lines) - 5} more rows")
            
if __name__ == "__main__":
    asyncio.run(main())