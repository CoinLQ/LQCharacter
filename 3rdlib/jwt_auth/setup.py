from setuptools import setup

setup(name='jwt_auth',
      version='0.1',
      description='The JWT AUTH API',
      url='http://github.com/CoinLQ/jwt_auth',
      author='Xiandian',
      author_email='xiandian1@gmail.com',
      license='MIT',
      packages=['jwt_auth'],
      install_requires=[
            'djangorestframework-jwt==1.11.0',
            'djangorestframework==3.6.3'
      ],
      zip_safe=False)