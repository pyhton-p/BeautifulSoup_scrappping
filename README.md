Website Summarizer
This project extracts and summarizes key information from a website using OpenAI's GPT model.

🔧 How It Works
Input a Main URL
You start by providing a website's main URL.

Extract Internal Links
The script collects up to 9 internal sub-URLs from the given website.

Fetch and Combine Text
It fetches plain text content from each URL and combines it into one large text block.

Summarize with OpenAI
The combined text is sent to OpenAI (GPT-3.5) to:

Generate a summary

Identify company name, industry, value proposition

Extract employees (like team members, directors, advisors)

Identify competitors

📦 Output
A structured JSON response containing all extracted details.

Printed WebsiteSummary object with title, summary, employees, and more.

🚀 Usage
Run the script:
bash

python your_script_name.py

Set your main URL inside the script in the main_url variable.
