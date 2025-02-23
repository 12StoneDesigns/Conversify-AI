from setuptools import setup, find_packages

setup(
    name="conversify-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "websockets==15.0",
        "jinja2==3.1.2",
        "python-dotenv==1.0.0",
    ],
)
