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

import pkg_resources
from suds.client import Client


class FlyDocService(object):
    """
    Base for FlyDoc services classes
    Loads the WSDL file at instanciation and defines some helpers to simplify written code
    """
    def __init__(self, wsdlFile):
        self.client = Client(wsdlFile)

    def _create(self, name, values=None):
        """
        Creates, and optioally populates, a new complex type instance
        """
        if values is None:
            values = {}

        value = self.client.factory.create(name)
        for key, val in values.items():
            value[key] = val

        return value

    def _getLastResponseHeaders(self):
        """
        Returns the headers of the last received response
        """
        return self.client.last_received().getChild('Envelope').getChild('Header')

    def _addHeader(self, headerName, headerValue):
        """
        Add a header for the soap query
        """
        headers = self.client.options.soapheaders
        if not isinstance(headers, dict):
            headers = {}
        headers.update({headerName: headerValue})
        self.client.set_options(soapheaders=headers)

    def __getattr__(self, name):
        """
        Binds method calls on the class, and all other calls prefixed by an underscore
        """
        if name.startswith('_') and hasattr(self.client, name[1:]):
            return getattr(self.client, name[1:])

        if hasattr(self.client.service, name):
            return getattr(self.client.service, name)

        raise AttributeError('Unknown attribute %s' % name)


class FlyDocSessionService(FlyDocService):
    """
    Session Service class
    """
    pass


class FlyDocSubmissionService(FlyDocService):
    """
    Submission Service class
    """
    def __init__(self, wsdlFile):
        super(FlyDocSubmissionService, self).__init__(wsdlFile)

        # Initialize enumeration constants
        self.ATTACHMENTS_FILTER = self.client.factory.create('ATTACHMENTS_FILTER')
        self.RESOURCE_TYPE = self.client.factory.create('RESOURCE_TYPE')
        self.WSFILE_MODE = self.client.factory.create('WSFILE_MODE')
        self.VAR_TYPE = self.client.factory.create('VAR_TYPE')


class FlyDocQueryService(FlyDocService):
    """
    Query Service class
    """
    def __init__(self, wsdlFile):
        super(FlyDocQueryService, self).__init__(wsdlFile)

        # Initialize enumeration constants
        self.ATTACHMENTS_FILTER = self.client.factory.create('ATTACHMENTS_FILTER')
        self.WSFILE_MODE = self.client.factory.create('WSFILE_MODE')
        self.VAR_TYPE = self.client.factory.create('VAR_TYPE')


class FlyDoc(object):
    """
    General FlyDoc class
    """
    def __init__(self, sessionServiceWsdlFile=None, submissionServiceWsdlFile=None, queryServiceWsdlFile=None):
        """
        Initialize services instances from WSDL files
        """
        if sessionServiceWsdlFile is None:
            sessionServiceWsdlFile = 'file://' + pkg_resources.resource_filename('flydoc', 'WSDL/SessionService.wsdl')
        if submissionServiceWsdlFile is None:
            submissionServiceWsdlFile = 'file://' + pkg_resources.resource_filename('flydoc', 'WSDL/SubmissionService.wsdl')
        if queryServiceWsdlFile is None:
            queryServiceWsdlFile = 'file://' + pkg_resources.resource_filename('flydoc', 'WSDL/QueryService.wsdl')

        self.sessionService = FlyDocSessionService(sessionServiceWsdlFile)
        self.submissionService = FlyDocSubmissionService(submissionServiceWsdlFile)
        self.queryService = FlyDocQueryService(queryServiceWsdlFile)

    def login(self, username, password):
        """
        Initialize the services by retrieving a session identifier
        """
        # Initialize services bindings
        bindings = self.sessionService.GetBindings(username)
        self.sessionService._set_options(location=bindings.sessionServiceLocation)
        self.submissionService._set_options(location=bindings.submissionServiceLocation)
        self.queryService._set_options(location=bindings.queryServiceLocation)

        # Call the login method
        self.loginInfo = self.sessionService.Login(userName=username, password=password)

        # Define the session header value
        SessionHeaderValue = self.sessionService._create('SessionHeader')
        SessionHeaderValue.sessionID = self.loginInfo.sessionID

        # Set the proper header values
        self.sessionService._addHeader('SessionHeaderValue', SessionHeaderValue)
        self.submissionService._addHeader('SessionHeaderValue', SessionHeaderValue)
        self.queryService._addHeader('SessionHeaderValue', SessionHeaderValue)

    def logout(self):
        """
        Close the connection with the services
        """
        self.sessionService.Logout()

    def browse(self, filter='msn=*', sortOrder='', attributes='', nItems=None, includeSubNodes=False, searchInArchive=False, reverse=False):
        """
        Generator used to browse transports
        """
        # Create QueryRequest object
        request = self.queryService._create('QueryRequest')
        # Request for transports one by one for the generator to work
        request.nItems = 1
        request.filter = filter
        request.sortOrder = sortOrder
        request.attributes = attributes
        request.includeSubNodes = includeSubNodes
        request.searchInArchive = searchInArchive

        # Request for the first or last item, depending on the order
        if not reverse:
            result = self.queryService.QueryFirst(request)
        else:
            result = self.queryService.QueryLast(request)

        totalNumber = result.nTransports
        # Check if there is at least one result
        if result.nTransports > 0:
            yield result.transports.Transport[0]

        # Add the queryID in headers (required)
        QueryHeaderValue = self.queryService._create('QueryHeader')
        QueryHeaderValue.queryID = self.queryService._getLastResponseHeaders().getChild('QueryHeaderValue').getChild('queryID').getText()
        self.queryService._addHeader('QueryHeaderValue', QueryHeaderValue)
        while(not result.noMoreItems and (nItems is not None and totalNumber < nItems)):
            # Request for the next item, depending on the order
            if not reverse:
                result = self.queryService.QueryNext(request)
            else:
                result = self.queryService.QueryPrevious(request)

            totalNumber += result.nTransports
            if result.nTransports > 0:
                yield result.transports.Transport[0]

    def browseAttachments(self, transportID, attachmentFilter=None, outputFileMode=None):
        """
        Generator used to browse attachments of a transport
        """
        for attachment in self.queryService.QueryAttachments(transportID, attachmentFilter, outputFileMode).attachments.Attachment:
            yield attachment

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
