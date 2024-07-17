# TI3115TU Template Repository

Welcome developers! If you've followed the Brightspace manual to set up your computer for Gitlab, this document will help you configure your project using Visual Studio Code.

## Setup / Configuration
* Preliminaries: Ensure you have Python 3, Git Bash, and Visual Studio Code installed. Follow the guidlines from https://brightspace.tudelft.nl/d2l/le/content/597832/Home.
* The TAs have explored various installation/configuration options, but this guide covers the essentials.
* If you encounter any issues, don't hesitate to ask a TA for assistance.

### Steup

1. Open VS code
2. Clone Git Repository
3. Open the terminal '^+\`' or 'ctrl+\`'

**Windows**
```bash
py -m venv env
.\env\Scripts\activate
py -m pip install -r requirements.txt
```
**Linux & Mac**
```bash
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
```

### Project Structure
* `scrum`: Contains your weelkly meeting notes
* `docs`: Contains project documentation, diagrams, and other relevant files.
* `project`: Holds most of your Python source files and tests. A sample Python program and example tests are provided.
* `test`: Contains the tests for your projects
* `.gitlab`: Contains the configuration for the user stories templte
* **DO NOT change the name of the `project` directory, as it could lead to issues with your CI pipeline.**

### Running
Run the sample code by opening `project/find.py` and selecting `Run python file in the terminal` from the context menu.

### Testing
You can also run tests through the terminal using the following command:
```
pytest
```

### Coverage
To check test coverage, use the following commands in the terminal:
```
coverage run -m pytest project
coverage report
```
To generate coverage documentation, run:
```
pytest --cov-config=.coveragerc --cov=project --cov-report=html project/test
```
The coverage report can be viewed by opening `htmlcov/index.html` in a web browser.

## Pylint
Check for coding style violations using `pylint` by running the following command in the terminal:
```
pylint project
```
Feel free to explore the code and check the output of Pylint, which might highlight any coding style issues.

Best of luck with your project development! If you need assistance at any point, don't hesitate to reach out to the TAs. Happy coding!