# Introduction 
This is the repo for the LamBots API. This repo contains that API/agent flow for LamBots, a one-stop-shop LLM application that will empower stakeholders at Lam by allowing them to configure custom LLM based applications and access key Lam data assets.

# Getting Started

## Backend
To run and test the LamBots API locally:

1. Install ODBC Driver 17 for your operating system from [this link](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16).

2. Install Python 3.11.1 from [the official Python website](https://www.python.org/downloads/release/python-3111/).

3. Add Python site packages path to environment variables:
   - For Windows: Right-click on "This PC" > Properties > Advanced system settings > Environment Variables > Under "User variables" click New
   - Variable name: PATH
   - Variable value: C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\Lib\site-packages
   - Click OK to save
   
   > **Note:** The Python path may differ depending on your installation location. To find your Python site-packages directory, you can run the following command in your terminal or command prompt:
   > ```python
   > python -c "import site; print(site.getsitepackages()[0])"
   > ```

4. Install Poetry (Steps below)

5. **NOTE:** Activating virtual environments in **PowerShell may not work** (because of security settings). It is recommended to use CMD.

## Poetry Installation Steps
```
cd ent-openai-lambots-api
python -m pip install pip_system_certs --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org
python -m pip install poetry
poetry config virtualenvs.in-project true
poetry install

# start the app
poetry run poe dev

```

## Package Management with poetry
Note: poetry will automatically create the new lock file for you. Just be certain to commit with your PR
```
# adding a package 
poetry add langchain 

# removing a package
poetry remove langchain
```

## Running in the Debugger
```
# get the path to your interpreter and use that in the debugger settings
poetry env list --full-path
```

## Frontend + Backend
The LamBot project consists of a FastAPI backend and the Hugging Face Chat UI frontend. Docker Compose is used to run both services together.


## JMeter Tests

For information on how to run JMeter tests, refer to the [JMeter README](jmeter/README.md).

# Build and Test
TODO: Describe and show how to build your code and run the tests. 

# Testing Framework
The project adops a clear separation of converns between unit tests and integration tests to ensure code quality, reliability, and maintainability.
## Tools & Libraries
- `pytest` Test runner and framework
- `pytest-mock` mocking support for unit tests
- `mongomock` In-memory MongoDB replacement for integration tests
- `fastpi.TestClient` HTTP client for testing FastAPI endpoints
## Unit Tests
- **Purpose**: Verify functionality in isolation
- **Location**: tests/unit/
- **Guidelines**: 
  - One-to-one mapping between test file and source file.
  - avoid external service/files/function/method calls
  - keep test cases small and fast
## Integration Tests
- **Purpose**: Validate interactions between components (e.g., DB, external methods/functions)
- **Location**: tests/integration/
- **Guidelines**
  - Cover end-to-end logic across components
  - avoid external services calls or external files

## Naming Conventions
### Test File Name
- Each test file follows the pattern **test_<module_name>.py**
- The test file path mirros the source structure of the module being tested
  - Example: src/services/auth_helpers.py -> tests/services/test_auth_helpers.py

### Test Class Naming
- Each module has a corresponding test class name that follows the pattern `class Test[ModuleName]`
- If a single module requires multiple logical test groups (e.g., different features, behaviors, or edge cases) use
the following pattern `class Test[ModuleName][TestGroupDescription]`

### Test Function Naming
- use descriptive names that reflect the method or scenario being tested
- use the following pattern `def test[method_under_test][expected_behavior_or_condition]`
## Running Tests
### Install required python3 Testing packages
`poetry install --with testing`
### Selecting tests to run
- runs all tests
  - `poetry run pytest` 
- run tests contained in child folder
  - `poetry run pytest tests/unit/core/utils`
- run testing module
  - `poetry run pytest tests/unit/core/utils/test_access_condition_helper.py` 
- run testing class
  - `poetry run pytest tests/unit/core/utils/test_access_condition_helper.py::TestAccessConditionChecks`
- run testing method
  - `poetry run pytest tests/unit/core/utils/test_access_condition_helper.py::TestAccessConditionChecks::test_required_tools_not_met`



# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)