from setuptools import setup, find_packages

setup(
    name="patrice_chonel",
    version="1.0",
    packages=find_packages(),
    package_data={'': ['employee_events.db', 'requirements.txt']},
    install_requires=[],

)
