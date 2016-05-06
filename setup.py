# -*- coding: utf-8 -*-
##############################################################################
#
#    pyFlyDoc, python library for FlyDoc webservices
#    Copyright (C) 2014 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of pyFlyDoc
#
#    pyFlyDoc is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyFlyDoc is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from distutils.core import setup

setup(
    name='pyFlyDoc',
    version='0.2.2',
    author='Sylvain Garancher',
    author_email='sylvain.garancher@syleam.fr',
    packages=['pyflydoc'],
    package_data={'pyflydoc': ['WSDL/*.wsdl']},
    scripts=[],
    #url='',
    license='LICENSE.txt',
    description='Python library for FlyDoc webservices',
    long_description=open('README.txt').read(),
    requires=[
        'suds_jurko (>=0.6)',
        'enum34',
    ],
    install_requires=[
        'suds_jurko >= 0.6',
        'enum34',
    ],
)
