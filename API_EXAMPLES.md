# API Examples - Biohacker Agent

Complete examples for calling the Biohacker Agent API with different health scenarios.

## Base URL

```
http://localhost:8000
```

## Endpoints

### POST /execute

Main endpoint for health recommendations.

---

## Example 1: High Blood Sugar (Pre-Diabetes)

**Scenario**: 45-year-old male software engineer with elevated glucose and HbA1c

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "My doctor said my blood sugar is too high. I want to prevent diabetes.",
      "userProfile": {
        "age": 45,
        "gender": "male",
        "job": "software engineer"
      },
      "bloodData": {
        "glucose": 115,
        "hba1c": 5.9,
        "ldl": 120,
        "hdl": 55,
        "triglycerides": 140,
        "crp": 2.5,
        "vitamin_d": 25,
        "insulin": 12
      },
      "pastMessages": []
    }
  }'
```

**Expected Recommendations**:
- Berberine supplementation
- Time-restricted eating (16:8)
- Daily walking routine

---

## Example 2: High Cholesterol & Cardiovascular Risk

**Scenario**: 52-year-old female accountant with high LDL and triglycerides

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "I have high cholesterol and my doctor wants me to improve it naturally before considering medication.",
      "userProfile": {
        "age": 52,
        "gender": "female",
        "job": "accountant"
      },
      "bloodData": {
        "glucose": 88,
        "hba1c": 5.2,
        "ldl": 145,
        "hdl": 45,
        "triglycerides": 180,
        "crp": 3.5,
        "vitamin_d": 30
      },
      "pastMessages": []
    }
  }'
```

**Expected Recommendations**:
- Omega-3 supplementation
- Mediterranean diet
- Daily walking or light exercise

---

## Example 3: Vitamin D Deficiency

**Scenario**: 35-year-old female office worker feeling fatigued

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "I feel tired all the time and work indoors. I rarely get sunlight.",
      "userProfile": {
        "age": 35,
        "gender": "female",
        "job": "office worker"
      },
      "bloodData": {
        "glucose": 85,
        "hba1c": 5.1,
        "ldl": 100,
        "hdl": 65,
        "triglycerides": 90,
        "crp": 1.0,
        "vitamin_d": 18
      },
      "pastMessages": []
    }
  }'
```

**Expected Recommendations**:
- Vitamin D3 supplementation (2000-4000 IU daily)
- Sun exposure recommendations
- Energy optimization strategies

---

## Example 4: Inflammation & Metabolic Syndrome

**Scenario**: 48-year-old male with multiple markers out of range

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "Multiple health markers are concerning. Want comprehensive improvement plan.",
      "userProfile": {
        "age": 48,
        "gender": "male",
        "job": "business executive"
      },
      "bloodData": {
        "glucose": 108,
        "hba1c": 5.7,
        "ldl": 135,
        "hdl": 42,
        "triglycerides": 165,
        "crp": 4.2,
        "vitamin_d": 22,
        "blood_pressure_systolic": 135,
        "blood_pressure_diastolic": 88
      },
      "pastMessages": []
    }
  }'
```

**Expected Recommendations**:
- Mediterranean diet or anti-inflammatory protocol
- HIIT or resistance training
- Stress management techniques

---

## Example 5: Optimal Health Check

**Scenario**: 28-year-old athlete with excellent markers

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "Just want to verify everything is optimal and see my longevity score.",
      "userProfile": {
        "age": 28,
        "gender": "male",
        "job": "professional athlete"
      },
      "bloodData": {
        "glucose": 80,
        "hba1c": 5.0,
        "ldl": 85,
        "hdl": 70,
        "triglycerides": 75,
        "crp": 0.5,
        "vitamin_d": 50,
        "insulin": 4
      },
      "pastMessages": []
    }
  }'
```

**Expected Response**:
- High longevity score (A or A+)
- Congratulatory message
- Maintenance recommendations
- No interventions needed

---

## Example 6: With Conversation History

**Scenario**: Follow-up conversation with context

```bash
curl -X POST "http://localhost:8000/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "userInput": "I tried walking more but still struggle with consistency. What else can I do?",
      "userProfile": {
        "age": 45,
        "gender": "male",
        "job": "software engineer"
      },
      "bloodData": {
        "glucose": 115,
        "hba1c": 5.9,
        "triglycerides": 140
      },
      "pastMessages": [
        {
          "role": "user",
          "content": "I want to improve my blood sugar"
        },
        {
          "role": "assistant",
          "content": "I recommend starting with a daily walking routine..."
        },
        {
          "role": "user",
          "content": "I have been walking but its not consistent"
        }
      ]
    }
  }'
```

**Expected Response**:
- Acknowledges walking difficulty
- Suggests easier alternatives (e.g., supplements like Berberine)
- Provides motivation strategies
- May recommend time-restricted eating as less time-intensive

---

## Response Structure

All responses follow this format:

```json
{
  "output": {
    "response": "Complete personalized message including:\n- Longevity score\n- Identified issues\n- Intervention recommendation\n- Scientific backing\n- 10-day challenge\n- Safety review\n- Medical disclaimers",
    "finalSuggestion": true
  }
}
```

### Fields Explained

- **`response`** (string): Complete markdown-formatted message for the user
  - Longevity score and grade
  - Analysis of problematic biomarkers
  - Personalized intervention recommendation
  - Scientific references with PMID
  - 10-day challenge details
  - Safety review results
  - Medical disclaimers

- **`finalSuggestion`** (boolean): Whether the recommendation was approved by the safety critic
  - `true`: Safe and appropriate, ready to implement
  - `false`: Rejected for safety reasons, consult healthcare provider

---

## Python Example

```python
import requests
import json

url = "http://localhost:8000/execute"

payload = {
    "input": {
        "userInput": "I want to improve my blood sugar levels",
        "userProfile": {
            "age": 45,
            "gender": "male",
            "job": "software engineer"
        },
        "bloodData": {
            "glucose": 115,
            "hba1c": 5.9,
            "ldl": 120,
            "hdl": 55,
            "triglycerides": 140,
            "crp": 2.5,
            "vitamin_d": 25
        },
        "pastMessages": []
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print("Longevity Score:", result["output"]["response"].split("score is")[1].split("/")[0].strip())
print("\nApproved:", result["output"]["finalSuggestion"])
print("\nFull Response:")
print(result["output"]["response"])
```

---

## JavaScript Example

```javascript
const axios = require('axios');

const url = 'http://localhost:8000/execute';

const payload = {
  input: {
    userInput: 'I want to improve my blood sugar levels',
    userProfile: {
      age: 45,
      gender: 'male',
      job: 'software engineer'
    },
    bloodData: {
      glucose: 115,
      hba1c: 5.9,
      ldl: 120,
      hdl: 55,
      triglycerides: 140,
      crp: 2.5,
      vitamin_d: 25
    },
    pastMessages: []
  }
};

axios.post(url, payload)
  .then(response => {
    console.log('Approved:', response.data.output.finalSuggestion);
    console.log('\nFull Response:');
    console.log(response.data.output.response);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

---

## Testing Tips

1. **Start Simple**: Test with one or two problematic biomarkers first
2. **Vary Ages**: Try different ages to see age-adjusted recommendations
3. **Include Context**: Add meaningful `userInput` for better personalization
4. **Use History**: Include `pastMessages` for follow-up conversations
5. **Check Approval**: Always verify `finalSuggestion` is `true` before implementing

---

## Common Biomarker Combinations

### Pre-Diabetes Profile
```json
{
  "glucose": 110-125,
  "hba1c": 5.7-6.4,
  "insulin": 10-20
}
```

### Cardiovascular Risk Profile
```json
{
  "ldl": 130-160,
  "hdl": 35-45,
  "triglycerides": 150-200,
  "crp": 2-5
}
```

### Metabolic Syndrome Profile
```json
{
  "glucose": 100-125,
  "triglycerides": 150+,
  "hdl": <40 (men) or <50 (women),
  "blood_pressure_systolic": 130+,
  "blood_pressure_diastolic": 85+
}
```

### Inflammation Profile
```json
{
  "crp": 3+,
  "triglycerides": elevated,
  "ldl": elevated
}
```

---

## Error Handling

### 503 - Graph Not Initialized
```json
{
  "detail": "Graph not initialized. Please wait for startup to complete."
}
```
**Solution**: Wait a few seconds after server start

### 500 - Execution Error
```json
{
  "detail": "Error executing graph: [error message]"
}
```
**Solution**: Check:
- OpenAI API key is valid
- Blood data uses correct field names
- User profile has required fields (age, gender, job)

### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "input", "userProfile", "age"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution**: Ensure all required fields are provided

---

## Rate Limits

OpenAI API has rate limits. For production:
- Implement request queuing
- Add retry logic with exponential backoff
- Cache similar requests
- Monitor usage at https://platform.openai.com/usage

---

## Next Steps

1. Try all example scenarios
2. Test with your own biomarker data
3. Experiment with conversation history
4. Integrate into your application
5. Customize prompts for your use case

For more information, see `BIOHACKER_README.md` and `QUICK_START.md`.

