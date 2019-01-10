try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='trackingmore',
    version='0.2',
    packages=['trackingmore',],
    author='Marco Esposito',
    author_email='marcoesposito1988@gmail.com',
    license='LGPLv3',
    description='Python wrapper for the TrackingMore API',
    url='https://github.com/marcoesposito1988/trackingmore-python',
    install_requires=['requests >= 0.8.8'],
    tests_require=['pytest'],
)
