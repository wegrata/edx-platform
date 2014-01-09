#   Copyright (c) 2008 Mikeal Rogers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distribuetd under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.template import RequestContext
from util.request import safe_get_host
from student.microsites import get_microsite_config, get_microsite_tpl_func
requestcontext = None


class MakoMiddleware(object):

    def process_request(self, request):
        global requestcontext
        requestcontext = RequestContext(request)
        requestcontext['is_secure'] = request.is_secure()
        requestcontext['site'] = safe_get_host(request)
        requestcontext['microsite'] = get_microsite_config(request)
        requestcontext['microsite_tpl'] = get_microsite_tpl_func(request)
