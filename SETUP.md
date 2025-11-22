# Windows Development Environment Setup

Complete setup guide for developing the AI Tamagotchi Health Companion on Windows 11.

## Phase 1: Core Development Tools (30 minutes)

### 1.1 DevEco Studio (CRITICAL)

**Download & Install:**
1. Visit: https://developer.huawei.com/consumer/en/deveco-studio
2. Download DevEco Studio for Windows (latest version supporting HarmonyOS API 18)
3. Run installer with admin privileges
4. **Installation path**: Choose a path WITHOUT spaces (e.g., `C:\DevEco`)

**Initial Configuration:**
```bash
# After first launch, install these SDK components:
- HarmonyOS SDK (API 18)
- OpenHarmony SDK (if available)
- ArkTS/ArkUI toolchain
- Wearable templates
```

**Verify Installation:**
1. Open DevEco Studio
2. Create New Project → Wearable → Empty Ability (ArkTS)
3. Check UI Previewer loads successfully

### 1.2 Conda Environment for AI Tools

**Install Miniconda (if not already):**
1. Download: https://docs.conda.io/en/latest/miniconda.html
2. Install to `C:\Users\<YourName>\miniconda3`
3. Add to PATH during installation

**Create Project Environment:**
```bash
# Open Anaconda Prompt (Start Menu → Anaconda Prompt)

# Create environment
conda create -n gemini_cli python=3.11 -y
conda activate gemini_cli

# Install AI SDKs
pip install anthropic google-generativeai

# Install AWS tools (for Reply challenge)
pip install boto3 sagemaker

# Install data science stack
pip install pandas numpy scikit-learn matplotlib jupyter

# Install development utilities
pip install requests python-dotenv rich typer
```

**Verify AI Setup:**
```bash
# Test Anthropic (Claude)
python -c "import anthropic; print('Claude SDK installed:', anthropic.__version__)"

# Test Google AI (Gemini)
python -c "import google.generativeai as genai; print('Gemini SDK installed')"
```

## Phase 2: API Keys & Authentication (15 minutes)

### 2.1 Environment Variables Setup

**Create `.env` file in project root:**
```bash
# In project directory (C:\Users\soere\DevecostudioProjects\CoolGroup)
# Create .env file with:

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google Gemini
GEMINI_API_KEY=your_gemini_key_here

# AWS (Reply hackathon credentials)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=eu-central-1

# Optional: Azure/Vertex (if using)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

**Secure the file:**
```bash
# Add to .gitignore
echo .env >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### 2.2 Get API Keys

**Anthropic Claude:**
1. Visit: https://console.anthropic.com/
2. Create account → API Keys → Create Key
3. Copy to `.env`

**Google Gemini:**
1. Visit: https://makersuite.google.com/app/apikey
2. Create API key
3. Copy to `.env`

**AWS (from Reply organizers):**
- Request credentials from Reply challenge coordinators at HackaTUM
- Should include Bedrock and SageMaker access

## Phase 3: Terminal AI Helper (20 minutes)

### 3.1 Create AI Query Script

**Create `tools/ai_helper.py`:**
```python
#!/usr/bin/env python3
"""
Terminal AI assistant for development queries.
Supports both Claude (Anthropic) and Gemini (Google).
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
import typer

# Load environment variables
load_dotenv()

console = Console()
app = typer.Typer()

def query_claude(prompt: str) -> str:
    """Query Claude via Anthropic API."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""You are an expert in HarmonyOS/OpenHarmony development with ArkTS and ArkUI.

Context: We're building an AI Tamagotchi health companion for Huawei Watch 5.

Question: {prompt}

Provide a concise, technical answer with code examples if relevant."""
        }]
    )

    return message.content[0].text

def query_gemini(prompt: str) -> str:
    """Query Gemini via Google AI API."""
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    response = model.generate_content(f"""You are an expert in HarmonyOS/OpenHarmony development.

Context: Building an AI Tamagotchi for Huawei Watch 5.

Question: {prompt}

Provide a concise answer with code examples.""")

    return response.text

@app.command()
def ask(
    query: str = typer.Argument(..., help="Your development question"),
    model: str = typer.Option("claude", "--model", "-m", help="AI model: claude or gemini")
):
    """Ask an AI assistant for development help."""

    console.print(f"\n[bold cyan]Querying {model}...[/bold cyan]\n")

    try:
        if model.lower() == "claude":
            response = query_claude(query)
        elif model.lower() == "gemini":
            response = query_gemini(query)
        else:
            console.print("[bold red]Error:[/bold red] Model must be 'claude' or 'gemini'")
            return

        # Render markdown response
        md = Markdown(response)
        console.print(md)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("\n[yellow]Check your API keys in .env file[/yellow]")

@app.command()
def test():
    """Test API connectivity for both models."""

    console.print("\n[bold]Testing AI API connections...[/bold]\n")

    # Test Claude
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        console.print("[green]✓[/green] Claude API key valid")
    except Exception as e:
        console.print(f"[red]✗[/red] Claude API error: {str(e)}")

    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        console.print("[green]✓[/green] Gemini API key valid")
    except Exception as e:
        console.print(f"[red]✗[/red] Gemini API error: {str(e)}")

if __name__ == "__main__":
    app()
```

### 3.2 Usage Examples

**Basic queries:**
```bash
# Activate environment
conda activate gemini_cli

# Ask Claude (default)
python tools/ai_helper.py ask "How do I access heart rate sensor in ArkTS?"

# Ask Gemini
python tools/ai_helper.py ask "Show me ArkUI state management example" --model gemini

# Test API connections
python tools/ai_helper.py test
```

**Create PowerShell alias (optional):**
```powershell
# Add to PowerShell profile ($PROFILE)
function Ask-AI {
    param([string]$query, [string]$model = "claude")
    conda activate gemini_cli
    python C:\Users\soere\DevecostudioProjects\CoolGroup\tools\ai_helper.py ask $query --model $model
}

# Usage: Ask-AI "How do I use DSoftBus?"
```

## Phase 4: AWS Setup (Reply Challenge)

### 4.1 Install AWS CLI

```powershell
# Download and install AWS CLI v2
# From: https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version

# Configure with Reply credentials
aws configure
# Enter AWS Access Key ID
# Enter AWS Secret Access Key
# Default region: eu-central-1
# Default output format: json
```

### 4.2 Test Bedrock Access

```python
# Create tools/test_bedrock.py
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='eu-central-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Hello from Huawei Watch app!"}
        ]
    })
)

print(json.loads(response['body'].read()))
```

```bash
# Run test
python tools/test_bedrock.py
```

## Phase 5: Git Configuration

```bash
# Set Git identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify setup
git status
git log
```

## Phase 6: Huawei Watch 5 Connection

### 6.1 Enable Developer Mode on Watch

1. **On Watch**: Settings → About → Software Info
2. **Tap "Build Number"** 7 times rapidly
3. **Developer Options** appears in settings
4. Enable **USB Debugging**
5. Enable **Stay awake when charging**

### 6.2 Windows USB Drivers

**Install Huawei HDB (HarmonyOS Debug Bridge):**
1. Included with DevEco Studio
2. Located in: `C:\DevEco\sdk\HarmonyOS-SDK\openharmony\<version>\toolchains\`
3. Add to PATH or use DevEco Studio terminal

**Test connection:**
```bash
# Connect watch via USB
# In DevEco Studio terminal:
hdc list targets

# Should show device ID
# If not, install watch drivers from Huawei website
```

## Phase 7: Project Structure Setup

```bash
cd C:\Users\soere\DevecostudioProjects\CoolGroup

# Create directory structure
mkdir -p watch-app/src/main/ets
mkdir -p watch-app/src/main/resources
mkdir -p cloud-backend/lambda
mkdir -p cloud-backend/sagemaker
mkdir -p docs
mkdir -p assets/animations

# Create README for each component
echo "# Watch Application (ArkTS)" > watch-app/README.md
echo "# Cloud Backend (AWS)" > cloud-backend/README.md
```

## Troubleshooting

### DevEco Studio won't start
- Check Java version (DevEco includes bundled JDK, use that)
- Run as administrator
- Disable antivirus temporarily during first launch

### HDB not detecting watch
- Try different USB port
- Use USB 2.0 port (not 3.0)
- Restart ADB/HDB: `hdc kill-server` then `hdc start-server`
- Check watch is unlocked and screen on

### Conda environment issues
```bash
# Reset environment
conda deactivate
conda env remove -n gemini_cli
# Re-create from Phase 1.2
```

### API key errors
```bash
# Verify .env file loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

## Next Steps

After setup is complete:
1. Read `PLAN.md` for development roadmap
2. Create initial DevEco Studio wearable project
3. Test terminal AI helper with technical questions
4. Begin Phase 1 (Foundation) from hackathon timeline

## Quick Reference

```bash
# Daily workflow startup
conda activate gemini_cli
cd C:\Users\soere\DevecostudioProjects\CoolGroup

# Open DevEco Studio
# Start → DevEco Studio

# Query AI during development
python tools/ai_helper.py ask "your question"

# Deploy to watch (in DevEco Studio)
# Run → Run 'entry' → Select Watch device
```
