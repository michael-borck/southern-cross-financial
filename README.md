# Southern Cross Financial

## Description

Southern Cross Financial is a sophisticated document generation and financial reporting system built on Jinja templating. This repository contains automated tools for generating professional financial reports, policy documents, and operational guides for Southern Cross Financial operations. The system leverages Jinja2 templating combined with Python, CSS, and JavaScript to produce consistent, data-driven financial documentation.

## Features

- **Automated Report Generation**: Generate professional financial reports using Jinja2 templates
- **Policy Documentation**: Comprehensive policy documents including conflicts of interest and privacy policies
- **Client Support Materials**: Onboarding checklists, financial planning guides, and SMSF administration resources
- **Employee Management**: Structured employee profiles and role-based documentation
- **Responsive Design**: CSS-based styling for web and print-ready documents
- **CI/CD Integration**: GitHub Actions workflow for automated deployment

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/michael-borck/southern-cross-financial.git
cd southern-cross-financial
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Verify the installation:
```bash
python -m scf --version
```

## Usage

### Generating Financial Reports

Use the report generator to create financial documents from templates:

```python
from scf.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate(
    template='financial_report.jinja',
    context={
        'client_name': 'John Doe',
        'report_date': '2024-01-15',
        'portfolio_value': 250000
    }
)
report.save('output/financial_report.html')
```

### Processing Templates

Templates are located in the `content/` directory and utilize Jinja2 syntax:

```jinja
<h1>{{ report_title }}</h1>
<p>Client: {{ client_name }}</p>
{% for item in portfolio_items %}
  <div>{{ item.name }}: ${{ item.value }}</div>
{% endfor %}
```

### Working with Policy Documents

Access and generate policy documentation:

```bash
python -m scf generate-policy --policy conflicts-of-interest-and-related-party-policy
```

### Client Support Materials

Generate client-facing documents:

```bash
python -m scf generate-support --document financial-planning-process-guide
python -m scf generate-support --document smsf-administration-guide
```

## Project Structure

```
southern-cross-financial/
├── .github/
│   └── workflows/           # CI/CD automation (GitHub Actions)
├── content/
│   ├── docs/
│   │   ├── policy/         # Policy documents
│   │   └── support/        # Client support materials
│   └── employees/          # Employee profiles and documentation
├── dist/                   # Distribution/build output
│   └── assets/            # CSS, JavaScript, and media files
├── brief.yaml             # Project configuration
├── LICENSE                # MIT License
└── README.md             # This file
```

## Configuration

The `brief.yaml` file contains project-level configuration:

```yaml
project:
  name: Southern Cross Financial
  version: 1.0.0
  author: michael-borck
  
templates:
  directory: content/
  output: dist/
```

## Policy Documents

- **Conflicts of Interest and Related Party Policy**: Guidelines for managing conflicts and related party transactions
- **Privacy and Client Data Protection Policy**: Comprehensive data protection and privacy standards

## Support Materials

- **Client Onboarding Checklist**: Step-by-step client onboarding process
- **Financial Planning Process Guide**: Detailed guide for financial planning procedures
- **SMSF Administration Guide**: Self-managed superannuation fund administration

## Deployment

The repository includes GitHub Actions workflow for automated deployment to GitHub Pages:

```yaml
# Automatically triggered on push to main branch
- Builds and validates templates
- Generates static output
- Deploys to GitHub Pages
```

View the workflow configuration in `.github/workflows/pages.yml`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a feature branch for your changes
2. Ensure all templates validate correctly
3. Update relevant documentation
4. Submit a pull request with a clear description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please use the GitHub Issues section of this repository.

## Author

**Michael Borck**

---

*Last updated: 2024*