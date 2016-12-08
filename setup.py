########
# Copyright (c) 2016 Antillion Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
import os
del os.link

from setuptools import setup

setup(
    name='cloudify-rundeck-plugin',

    version='0.1.2',
    author='Oliver Tupman',
    author_email='otupman@antillion.com',
    description='Rundeck Plugin for Cloudify',

    packages=['cfyrundeck'],

    license='LICENSE',
    zip_safe=False,
    install_requires=[
        "cloudify-plugins-common==3.4.0",
        "cloudify-dsl-parser==3.4.0",
        "arundeckrun==0.2.3"
    ],
    test_requires=[
        "cloudify-dsl-parser==3.4.0",
        "nose"
    ]
)
