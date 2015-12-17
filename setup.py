import os
from setuptools import setup, find_packages

setup(name="adi.keymaker",
      version="0.15.50",
      author="Advance Services",
      author_email="services@lists.advance.net",
      url='http://pypi.advance.net/packages/adi.keymaker',
      license='Proprietary',
      long_description=open(os.path.join(os.path.dirname(__file__),
                                         'README.md')).read(),
      entry_points={
          "console_scripts": [
              "keymaker = adi.keymaker.keymaker:main",
          ]
      },
      scripts=['adi/keymaker/scripts/keymaker-completion.bash'],
      packages=find_packages(),
      namespace_packages=['adi'],
      install_requires=["boto==2.38.0", "awscli>=1.7.22,<2"],
      include_package_data=True,
      extras_require={
          'test': ['mock'],
      }
)
