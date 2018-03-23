from setuptools import setup

setup(
    name='TenantUnionPlus',
    packages=['TenantUnionPlusServer'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
