from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import json

# Initialize OpenAI API with your API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Load this from environment variables or set it directly.

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic model for the shipping cost comparison request
class ShippingCostComparisonRequest(BaseModel):
    carriers: list
    num_examples: int = 5

# Function to call the OpenAI Chat API to generate shipping cost comparison data for carriers
def get_shipping_cost_comparison(carriers, num_examples=5):
    prompt = f"""Generate shipping cost comparison data for the following carriers: {', '.join(carriers)}.
    Create {num_examples} realistic shipping scenarios with varying weights, dimensions, and locations.
    For each scenario, provide the shipping cost for each carrier, and calculate the average savings and percent savings when using the cheapest option.
    
    Return the data as a JSON string with this structure containing 4 different zones:
    {{
      "data": [
        {{
            "Distance": "Zone 1",
            "fedex": 12.04,
            "ups": 6.99,
            "usps": 6.77,
            "orchestro": 5.85
        }},
        ...
      ]
    }}
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates realistic shipping carrier data."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)

@app.post("/shipping-cost-comparison/")
async def shipping_cost_comparison(request: ShippingCostComparisonRequest):
    # Call the function to get the shipping cost comparison data
    cost_comparison_data = get_shipping_cost_comparison(request.carriers, request.num_examples)
    
    # Return the response data
    return cost_comparison_data

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shipping Cost Comparison API!"}
