from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
    setup(
        name = 'lazyshorts-py', # FIXME: sync with __main__.py
        version = '0.0.1',
        author = 'Gergő Vári',
        author_email = 'work@varigergo.xyz',
        license = 'GNU LESSER GENERAL PUBLIC LICENSE 3',
        description = 'A command to convert long-form videos into multiple short-form videos, with burned-in text and subtitles.',
        long_description = long_description,
        long_description_content_type = "text/markdown",
        url = 'https://github.com/gergovari/lazyshorts-py',
        packages = find_packages(),
        install_requires = [requirements],
        python_requires='>=3.7',
        classifiers=[
            "Programming Language :: Python :: 3.8",
            "Operating System :: OS Independent",
        ],
        dependency_links = [
            "https://download.pytorch.org/whl/torch_stable.html"
        ],
        entry_points = '''
            [console_scripts]
            lazyshorts=main:main
        '''
    )
