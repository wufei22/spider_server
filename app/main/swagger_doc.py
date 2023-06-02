from flask_restx import Api, Resource, fields
from flask import Blueprint

blueprint1 = Blueprint('api', __name__)
api = Api(blueprint1, version="1.0", title="Crawled API", description="A simple Crawled API", )

is_homepage = api.model(
    "is_homepage", {"is_homepage": fields.Boolean(required=True, description="是否为首页地址")}
)
get_column = api.model(
    "get_column", {"task_status": fields.Boolean(required=True, description="任务是否开始执行")}
)
check_xpath = api.model(
    "check_xpath", {"xpath_config": fields.Boolean(required=True, description="xpath是否可用")}
)
start_task = api.model(
    "start_task", {"task_status": fields.Boolean(required=True, description="任务是否开始执行")}
)
end_task = api.model(
    "end_task", {"task_status": fields.Boolean(required=True, description="任务是否中止")}
)


@api.route("/isHomepage")
@api.doc(params={"website_url": "The website url"})
class IsHomepage(Resource):
    """判url是否为网站首页的api"""

    @api.marshal_with(is_homepage, envelope='data')
    def post(self):
        return is_homepage


@api.route("/getColumn")
@api.doc(params={"website_id": "The website id"})
class GetColumn(Resource):
    """分析栏目的接口"""

    @api.marshal_with(get_column, envelope='data')
    def post(self):
        return get_column


@api.route("/checkXpath")
@api.doc(params={"input_url": "url地址", "xpath": "xpath地址"})
class CheckXpath(Resource):
    """测试xpath的接口"""

    @api.marshal_with(check_xpath, envelope='data')
    def post(self):
        return check_xpath


@api.route("/startTask")
class StartTask(Resource):
    """开始爬虫任务的接口"""

    @api.marshal_with(start_task, envelope='data')
    def get(self):
        return start_task


@api.route("/endTask")
class EndTask(Resource):
    """结束爬虫任务的接口"""

    @api.marshal_with(end_task, envelope='data')
    def get(self):
        return end_task
