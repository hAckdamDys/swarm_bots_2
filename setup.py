from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('readme.md') as f:
    readme = f.read()

setup(name='swarm_bots',
      version='0.3',
      description='Multi-robot system coordination using swarm intelligence.',
      long_description=readme,
      url='https://github.com/hAckdamDys/swarm_bots_2',
      author='Adam Dyszy',
      author_email='electro.ubro@gmail.com',
      license='MIT',
      install_requires=requirements,
      packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'use_cases*'])
      )
