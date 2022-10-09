import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sharingan",
    version="0.0.5",
    author="s045pd",
    author_email="s045pd.x@gmail.com",
    description="We will try to find your visible basic footprint from social media as much as possible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python_box==4.2.3",
        "requests_html==0.10.0",
        "termcolor==1.1.0",
        "Click==7.0",
        "httpx==0.13.3",
        "progressbar33==2.4",
        "moment==0.8.2",
        "retry==0.9.2",
        "pypeln==0.4.4",
    ],
)
