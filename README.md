# Specmatic Sample: Python-Flask Order API

* [Specmatic Website](https://specmatic.io)
* [Specmatic Documentation](https://docs.specmatic.io)

This sample project illustrates the implementation of contract-driven development and contract testing within a Flask (Python) application. In this context, Specmatic is utilized to function as a client, making calls to API service according to its OpenAPI specification to validate  its functionality.

Here is the API's [contract/open api spec](https://github.com/specmatic/specmatic-order-contracts/blob/main/io/specmatic/examples/store/openapi/api_order_v3.yaml)

## Tech

1. Flask
2. Specmatic
3. PyTest
4. Coverage
5. Docker Desktop

## Setup

1. Install [Python 3.12](https://www.python.org/)
2. Install JRE 17 or later.
3. Install Docker Desktop

## Setup Virtual Environment

1. ### Create a virtual environment named ".venv" by executing the following command in the terminal from the project's root directory

   ```shell
    python -m venv .venv
    ```

2. ### Activate virtual environment by executing

* **on MacOS and Linux**

   ```shell
   source .venv/bin/activate
   ```

* **on Windows CMD**

  ```cmd
  .venv\Scripts\activate.bat
  ```

* **on Windows Powershell (you may need to adjust the ExecutionPolicy)**

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

## Install Dependencies

To install all necessary dependencies for this project, navigate to the project's root directory in your terminal and execute

```shell
pip install -r requirements.txt
```

## Execute Tests and Validate Contracts with Specmatic

Executing this command will initiate Specmatic and execute the tests on the Flask application.

```shell
pytest test -v -s
```
