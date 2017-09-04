##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import logging
import json

from tornado import web
from tornado import gen

from opnfv_testapi.common.config import CONF
from opnfv_testapi.resources import handlers
from opnfv_testapi.resources import application_models
from opnfv_testapi.tornado_swagger import swagger
from opnfv_testapi.ui.auth import constants as auth_const


class GenericApplicationHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericApplicationHandler, self).__init__(application,
                                                        request,
                                                        **kwargs)
        self.table = "applications"
        self.table_cls = application_models.Application


class ApplicationsCLHandler(GenericApplicationHandler):
    @swagger.operation(nickname="queryApplications")
    def get(self):
        """
            @description: Retrieve result(s) for a application project
                          on a specific pod.
            @notes: Retrieve result(s) for a application project on a specific pod.
                Available filters for this request are :
                 - id  : Application id
                 - period : x last days, incompatible with from/to
                 - from : starting time in 2016-01-01 or 2016-01-01 00:01:23
                 - to : ending time in 2016-01-01 or 2016-01-01 00:01:23
                 - signed : get logined user result

                GET /results/project=funcapplication&case=vPing&version=Arno-R1 \
                &pod=pod_name&period=15&signed
            @return 200: all application results consist with query,
                         empty list if no result is found
            @rtype: L{Applications}
        """
        def descend_limit():
            descend = self.get_query_argument('descend', 'true')
            return -1 if descend.lower() == 'true' else 1

        def last_limit():
            return self.get_int('last', self.get_query_argument('last', 0))

        def page_limit():
            return self.get_int('page', self.get_query_argument('page', 0))

        limitations = {
            'sort': {'_id': descend_limit()},
            'last': last_limit(),
            'page': page_limit(),
            'per_page': CONF.api_results_per_page
        }

        self._list(query=self.set_query(), **limitations)
        logging.debug('list end')

    @swagger.operation(nickname="createApplication")
    def post(self):
        """
            @description: create a application
            @param body: application to be created
            @type body: L{ApplicationCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: application is created.
            @raise 404: pod/project/applicationcase not exist
            @raise 400: body/pod_name/project_name/case_name not provided
        """
        openid = self.get_secure_cookie(auth_const.OPENID)
        if openid:
            self.json_args['owner'] = openid

        self._post()

    def _post(self):
        miss_fields = []
        carriers = []

        self._create(miss_fields=miss_fields, carriers=carriers)


class ApplicationsGURHandler(GenericApplicationHandler):
    @swagger.operation(nickname="updateApplicationById")
    def put(self, application_id):
        """
            @description: update a single application by id
            @param body: fields to be updated
            @type body: L{ApplicationUpdateRequest}
            @in body: body
            @rtype: L{Application}
            @return 200: update success
            @raise 404: Application not exist
            @raise 403: nothing to update
        """
        data = json.loads(self.request.body)
        item = data.get('item')
        value = data.get(item)
        logging.debug('%s:%s', item, value)
        try:
            self.update(application_id, item, value)
        except Exception as e:
            logging.error('except:%s', e)
            return

    @web.asynchronous
    @gen.coroutine
    def update(self, application_id, item, value):
        self.json_args = {}
        self.json_args[item] = value
        query = {'_id': application_id, 'owner': self.get_secure_cookie(auth_const.OPENID)}
        db_keys = ['_id', 'owner']
        self._update(query=query, db_keys=db_keys)