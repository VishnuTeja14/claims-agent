# Autonomous Insurance Claims Processing Agent

This agent is designed to automate the initial intake of insurance claims from First Notice of Loss (FNOL) documents. It extracts key information, identifies missing data, and routes claims to appropriate workflows based on predefined business rules.

## Features

- **Field Extraction**: Uses LLM-based extraction (supporting both text and multimodal PDF analysis) to capture policy, incident, party, and asset details.
- **Data Validation**: Automatically identifies missing mandatory fields.
- **Intelligent Routing**: Routes claims based on:
  - **Fast-track**: Claims with estimated damage < $25,000.
  - **Manual Review**: Claims with missing mandatory fields.
  - **Investigation Flag**: Claims with descriptions suggesting fraud or inconsistency.
  - **Specialist Queue**: Claims involving injuries.
- **Reasoning**: Provides a clear explanation for every routing decision.

## Requirements

- Python 3.11+
- `openai` library
- `pdf2image` and `pypdf` libraries
- `poppler-utils` (for PDF processing)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd claims-agent
   ```

2. Install dependencies:
   ```bash
   pip install openai pdf2image pypdf
   ```

3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

## Usage

Run the agent on a PDF or text FNOL document:

```bash
python main.py data/sample_claim.pdf
```

### Example Output

```json
{
  "extractedFields": {
    "policy_number": "POL123456",
    "policyholder_name": "John Doe",
    ...
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($1500.0) is below $25,000 threshold."
}
```

## Approach

1. **Extraction**: The agent uses `gpt-4.1-mini` for robust extraction. For PDF documents, it utilizes a multimodal approach (converting the first page to an image) to handle complex form layouts that traditional OCR might struggle with.
2. **Routing Logic**: A rule-based engine processes the extracted fields to determine the workflow. This ensures consistency and transparency.
3. **Modularity**: The system is split into an `agent.py` for logic and `utils.py` for document processing, making it easy to extend.
