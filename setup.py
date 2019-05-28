from setuptools import setup

with open('readme.md') as f:
    readme = f.read()

setup(name='swarm_bots',
      version='0.1',
      description='Multi-robot system coordination using swarm intelligence.',
      long_description=readme,
      url='https://github.com/hAckdamDys/swarm_bots_2',
      author='Adam Dyszy',
      author_email='electro.ubro@gmail.com',
      license='MIT',
      packages=['swarm_bots']
      )
