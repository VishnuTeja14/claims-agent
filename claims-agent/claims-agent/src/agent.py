import json
import os
import re
import base64
from openai import OpenAI
from pdf2image import convert_from_path

client = OpenAI()

class ClaimsAgent:
    def __init__(self):
        self.mandatory_fields = [
            "policy_number", "policyholder_name", "date_of_loss", 
            "location", "description", "claim_type", "initial_estimate"
        ]

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_fields_from_text(self, text):
        prompt = f"""
        Extract the following fields from the provided insurance FNOL document text.
        If a field is not found, return null.
        
        Fields to extract:
        - policy_number
        - policyholder_name
        - effective_dates (start and end if available)
        - date_of_loss
        - time_of_loss
        - location
        - description
        - claimant_name
        - third_parties (list)
        - contact_details
        - asset_type
        - asset_id (e.g. VIN)
        - estimated_damage (numeric value)
        - claim_type (e.g. collision, theft, injury, etc.)
        - attachments (list of names if mentioned)
        - initial_estimate (numeric value)

        Text:
        {text}

        Return ONLY a JSON object.
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def extract_fields_multimodal(self, pdf_path):
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        temp_image_path = "/tmp/fnol_page1.png"
        images[0].save(temp_image_path, "PNG")
        
        base64_image = self.encode_image(temp_image_path)
        
        prompt = """
        Extract the following fields from this insurance FNOL document.
        If a field is not found or is blank, return null.
        
        Fields to extract:
        - policy_number
        - policyholder_name
        - effective_dates (start and end if available)
        - date_of_loss
        - time_of_loss
        - location
        - description
        - claimant_name
        - third_parties (list)
        - contact_details
        - asset_type
        - asset_id (e.g. VIN)
        - estimated_damage (numeric value)
        - claim_type (e.g. collision, theft, injury, etc.)
        - attachments (list of names if mentioned)
        - initial_estimate (numeric value)

        Return ONLY a JSON object.
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def get_route(self, fields):
        missing_fields = [f for f in self.mandatory_fields if not fields.get(f)]
        
        if missing_fields:
            return "Manual Review", f"Missing mandatory fields: {', '.join(missing_fields)}", missing_fields

        # Check for fraud/inconsistency
        description = str(fields.get("description", "")).lower()
        fraud_keywords = ["fraud", "inconsistent", "staged"]
        if any(word in description for word in fraud_keywords):
            return "Investigation Flag", "Description contains suspicious keywords (fraud, inconsistent, staged).", []

        # Check for injury
        claim_type = str(fields.get("claim_type", "")).lower()
        if "injury" in claim_type:
            return "Specialist Queue", "Claim involves injuries, routed to specialist.", []

        # Check estimate for fast-track
        try:
            estimate_val = fields.get("initial_estimate")
            if estimate_val is not None:
                estimate = float(re.sub(r'[^\d.]', '', str(estimate_val)))
                if estimate < 25000:
                    return "Fast-track", f"Estimated damage (${estimate}) is below $25,000 threshold.", []
        except (ValueError, TypeError):
            pass

        return "Standard Processing", "Claim meets all requirements for standard workflow.", []

    def process_claim(self, file_path):
        if file_path.endswith('.pdf'):
            extracted_fields = self.extract_fields_multimodal(file_path)
        else:
            with open(file_path, 'r') as f:
                text = f.read()
            extracted_fields = self.extract_fields_from_text(text)
            
        route, reasoning, missing = self.get_route(extracted_fields)
        
        return {
            "extractedFields": extracted_fields,
            "missingFields": missing,
            "recommendedRoute": route,
            "reasoning": reasoning
        }
